# cms/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import logging
from django.db import transaction

from .models import (
    Submission, Challenge, PointTransaction, Ranking,
    Assignment, Quiz, Workshop, TimelineEvent, Enrollment,
    Session, Post, Article, Video
)
from ums.models import Profile

logger = logging.getLogger(__name__)

# Helper Functions
def create_point_transaction(user, transaction_type, points, description):
    """
    Creates a PointTransaction instance.
    """
    PointTransaction.objects.create(
        user=user,
        transaction_type=transaction_type,
        points=points,
        description=description
    )
    logger.info(
        f"PointTransaction ({transaction_type.capitalize()}) created for User={user.username}, Points={points}"
    )

def update_ranking_and_profile(user, points, transaction_type):
    """
    Updates the user's Ranking and Profile based on points earned or spent.
    """
    # Update Ranking
    ranking, created = Ranking.objects.get_or_create(user=user)
    ranking.points += points if transaction_type == 'earn' else 0
    ranking.save()
    logger.info(
        f"Ranking updated for User={user.username}: Total Points={ranking.points}"
    )

    # Update Profile
    user.total_points += points if transaction_type == 'earn' else -points
    user.save()
    logger.info(
        f"Profile updated for User={user.username}: Total Points={user.total_points}"
    )

def create_timeline_events(user, event_type, content_object, event_date):
    """
    Creates a TimelineEvent instance.
    """
    TimelineEvent.objects.create(
        user=user,
        event_type=event_type,
        content=content_object,
        event_date=event_date
    )
    logger.info(f"TimelineEvent ({event_type}) created for {content_object.title} on {event_date}")

def bulk_create_timeline_events(users, event_type, content_object, event_date):
    """
    Bulk creates TimelineEvent instances.
    """
    timeline_events = [
        TimelineEvent(
            user=user,
            event_type=event_type,
            content_object=content_object,
            event_date=event_date
        )
        for user in users
    ]
    TimelineEvent.objects.bulk_create(timeline_events)
    logger.info(f"Bulk TimelineEvents ({event_type}) created for {content_object.title} on {event_date}")

# Signal Handlers

# 1. Handle User Creation: Create Ranking and Profile
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_ranking_and_profile(sender, instance, created, **kwargs):
    if created:
        # Use get_or_create to prevent duplicates
        Ranking.objects.get_or_create(user=instance, defaults={'points': 0})
        Profile.objects.get_or_create(user=instance)
        logger.info(f"Ranking and Profile created for new User={instance.username}")

# 2. Handle Submission Grade
@receiver(post_save, sender=Submission)
def handle_submission_grade(sender, instance, created, **kwargs):
    user = instance.user
    current_grade = instance.grade

    # Fetch previous grade before save
    if not created:
        try:
            previous_grade = Submission.objects.get(pk=instance.pk).grade
        except Submission.DoesNotExist:
            previous_grade = None
    else:
        previous_grade = None

    # Only proceed if the grade has changed or if this is a new submission
    if created or (previous_grade != current_grade):
        with transaction.atomic():
            points_earned = 0
            points_spent = 0
            description = ''
            transaction_type = ''

            # Reverse previous points if they exist and grade has changed
            if not created and previous_grade is not None:
                previous_points_earned, previous_points_spent = calculate_points(previous_grade, instance)
                if previous_points_earned > 0:
                    reverse_transaction(user, 'earn', previous_points_earned)
                if previous_points_spent > 0:
                    reverse_transaction(user, 'spend', previous_points_spent)

            # Calculate new points based on the current grade
            points_earned, points_spent = calculate_points(current_grade, instance)
            content_object = instance.content_object
            content_model = content_object.__class__.__name__.lower()

            logger.info(
                f"Processing Submission Update: User={user.username}, "
                f"Previous Grade={previous_grade}, Current Grade={current_grade}, "
                f"Points Earned={points_earned}, Points Spent={points_spent}"
            )

            # Handle earning points
            if points_earned > 0:
                title = content_object.title
                description = f'Earned {points_earned} points for {content_model}: {title}'
                transaction_type = 'earn'
                create_point_transaction(user, transaction_type, points_earned, description)
                update_ranking_and_profile(user, points_earned, transaction_type)

            # Handle spending points
            if points_spent > 0:
                if user.total_points >= points_spent:
                    transaction_type = 'spend'
                    description = f"Spent {points_spent} points for {content_model}: {content_object.title}"
                    create_point_transaction(user, transaction_type, points_spent, description)
                    update_ranking_and_profile(user, points_spent, transaction_type)
                else:
                    logger.warning(
                        f"User={user.username} does not have enough points to perform the action: {content_object.title}"
                    )
                    # Optionally, handle insufficient points (e.g., notify the user or revert the submission)

def calculate_points(grade, instance):
    """Helper function to determine points based on grade and submission type."""
    # Return 0 points if grade is None to avoid TypeError
    if grade is None:
        return 0, 0

    points_earned = 0
    points_spent = 0
    content_object = instance.content_object
    content_model = content_object.__class__.__name__.lower()

    if content_model == 'assignment':
        if grade >= 90:
            points_earned = content_object.points
        elif grade >= 75:
            points_earned = content_object.points // 2
        if grade < 50:
            points_spent = content_object.points // 4
    elif content_model == 'quiz':
        if grade >= 90:
            points_earned = content_object.points
        elif grade >= 75:
            points_earned = content_object.points // 2
        if grade < 50:
            points_spent = content_object.points // 4
    elif content_model == 'challenge':
        points_earned = content_object.points
    elif content_model == 'workshop':
        points_spent = content_object.points_cost

    return points_earned, points_spent

def reverse_transaction(user, transaction_type, points):
    """Reverse a transaction by deducting or restoring points accordingly."""
    if transaction_type == 'earn':
        create_point_transaction(user, 'reverse_earn', -points, "Reversed points for updated grade")
        update_ranking_and_profile(user, points, 'spend')
    elif transaction_type == 'spend':
        create_point_transaction(user, 'reverse_spend', points, "Restored points for updated grade")
        update_ranking_and_profile(user, points, 'earn')

# 3. Handle Challenge Creation: Create TimelineEvents for Start and Deadline
@receiver(post_save, sender=Challenge)
def handle_challenge_creation(sender, instance, created, **kwargs):
    if not created:
        return  # Only process on creation

    logger.info(f"New Challenge Created: {instance.title}")

    # Fetch all users enrolled in the course
    enrollments = Enrollment.objects.filter(course=instance.course).select_related('user')
    users = [enrollment.user for enrollment in enrollments]

    # Create TimelineEvents for Challenge Start
    challenge_start_date = timezone.make_aware(timezone.datetime.combine(instance.date, timezone.datetime.min.time()))
    bulk_create_timeline_events(users, 'challenge_start', instance, challenge_start_date)

    # Create TimelineEvents for Challenge Deadline
    challenge_deadline_date = instance.due_date
    bulk_create_timeline_events(users, 'challenge_deadline', instance, challenge_deadline_date)

# 4. Handle Assignment Creation: Create TimelineEvents
@receiver(post_save, sender=Assignment)
def create_assignment_timeline_event(sender, instance, created, **kwargs):
    if not created:
        return  # Only process on creation

    logger.info(f"Assignment Created: {instance.title}")

    # Fetch all users enrolled in the course
    enrollments = Enrollment.objects.filter(course=instance.course).select_related('user')
    users = [enrollment.user for enrollment in enrollments]

    # Create TimelineEvents for Assignment Deadline
    bulk_create_timeline_events(users, 'assignment', instance, instance.due_date)

# 5. Handle Quiz Creation: Create TimelineEvents
@receiver(post_save, sender=Quiz)
def create_quiz_timeline_event(sender, instance, created, **kwargs):
    if not created:
        return  # Only process on creation

    if not hasattr(instance, 'due_date'):
        logger.error(f"Quiz instance {instance.title} lacks 'due_date' field.")
        return

    logger.info(f"Quiz Created: {instance.title}")

    # Fetch all users enrolled in the course
    enrollments = Enrollment.objects.filter(course=instance.course).select_related('user')
    users = [enrollment.user for enrollment in enrollments]

    # Create TimelineEvents for Quiz Deadline
    bulk_create_timeline_events(users, 'quiz', instance, instance.due_date)

# 6. Handle Workshop Creation: Create TimelineEvents
@receiver(post_save, sender=Workshop)
def create_workshop_timeline_event(sender, instance, created, **kwargs):
    if not created:
        return  # Only process on creation

    logger.info(f"Workshop Created: {instance.title}")

    # Fetch all users enrolled in the course
    enrollments = Enrollment.objects.filter(course=instance.course).select_related('user')
    users = [enrollment.user for enrollment in enrollments]

    # Create TimelineEvents for Workshop Meeting
    bulk_create_timeline_events(users, 'workshop', instance, instance.date_time)

# 7. Handle Session Creation: Create TimelineEvents
@receiver(post_save, sender=Session)
def create_session_timeline_event(sender, instance, created, **kwargs):
    if not created:
        return  # Only process on creation

    logger.info(f"Session Created: {instance.title}")

    # Fetch all users enrolled in the course
    enrollments = Enrollment.objects.filter(course=instance.course).select_related('user')
    users = [enrollment.user for enrollment in enrollments]

    # Create TimelineEvents for Session Meeting
    bulk_create_timeline_events(users, 'session', instance, instance.date_time)

# 8. Handle Assignment Deletion: Delete TimelineEvents
@receiver(post_delete, sender=Assignment)
def delete_assignment_timeline_events(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    TimelineEvent.objects.filter(
        content_type=content_type,
        object_id=instance.id,
        event_type='assignment'
    ).delete()
    logger.info(f"TimelineEvents deleted for Assignment: {instance.title}")

# 9. Handle Quiz Deletion: Delete TimelineEvents
@receiver(post_delete, sender=Quiz)
def delete_quiz_timeline_events(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    TimelineEvent.objects.filter(
        content_type=content_type,
        object_id=instance.id,
        event_type='quiz'
    ).delete()
    logger.info(f"TimelineEvents deleted for Quiz: {instance.title}")

# 10. Handle Workshop Deletion: Delete TimelineEvents
@receiver(post_delete, sender=Workshop)
def delete_workshop_timeline_events(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    TimelineEvent.objects.filter(
        content_type=content_type,
        object_id=instance.id,
        event_type='workshop'
    ).delete()
    logger.info(f"TimelineEvents deleted for Workshop: {instance.title}")

# 11. Handle Session Deletion: Delete TimelineEvents
@receiver(post_delete, sender=Session)
def delete_session_timeline_events(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    TimelineEvent.objects.filter(
        content_type=content_type,
        object_id=instance.id,
        event_type='session'
    ).delete()
    logger.info(f"TimelineEvents deleted for Session: {instance.title}")
