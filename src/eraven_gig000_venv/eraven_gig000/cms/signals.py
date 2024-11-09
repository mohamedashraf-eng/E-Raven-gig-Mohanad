# cms/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Submission, Challenge, PointTransaction, Ranking
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Submission)
def handle_submission_grade(sender, instance, created, **kwargs):
    if instance.grade is not None:
        # Simple grading logic: award points based on grade
        if instance.grade >= 90:
            points = 10
        elif instance.grade >= 75:
            points = 5
        else:
            points = 0

        if instance.challenge:
            points = instance.challenge.points
            
        logger.info(f"Processing Submission: User={instance.user.username}, Grade={instance.grade}, Points={points}")

        # Determine the submission type and set the description
        if points > 0:
            if instance.assignment:
                title = instance.assignment.title
                description = f'Earned {points} points for high grade on assignment: {title}'
            elif instance.quiz:
                title = instance.quiz.title
                description = f'Earned {points} points for high grade on quiz: {title}'
            elif instance.challenge:
                title = instance.challenge.title
                description = f'Earned {points} points for completing challenge: {title}'
            else:
                description = f'Earned {points} points for high grade on an unknown task'

            # Create the PointTransaction entry
            PointTransaction.objects.create(
                user=instance.user,
                transaction_type='earn',
                points=points,
                description=description
            )
            logger.info(f"PointTransaction created for User={instance.user.username}, Points={points}")

            # Update Ranking
            ranking, created_rank = Ranking.objects.get_or_create(user=instance.user)
            ranking.points += points
            ranking.save()
            logger.info(f"Ranking updated for User={instance.user.username}: Total Points={ranking.points}")

@receiver(post_save, sender=Challenge)
def handle_challenge_creation(sender, instance, created, **kwargs):
    if created:
        # Optionally, notify users about new challenges
        logger.info(f"New Challenge Created: {instance.title}")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_ranking(sender, instance, created, **kwargs):
    if created:
        Ranking.objects.get_or_create(user=instance)
        logger.info(f"Ranking created for new User={instance.username}")
