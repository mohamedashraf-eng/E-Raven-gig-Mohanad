# cms/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Submission, Challenge, PointTransaction, Ranking
from django.conf import settings

@receiver(post_save, sender=Submission)
def handle_submission_grade(sender, instance, created, **kwargs):
    if not created and instance.grade is not None:
        # Simple grading logic: award points based on grade
        if instance.grade >= 90:
            points = 10
        elif instance.grade >= 75:
            points = 5
        else:
            points = 0

        # Determine the submission type and set the description
        if points > 0:
            if instance.assignment:
                title = instance.assignment.title
                description = f'Earned {points} points for high grade on assignment: {title}'
            elif instance.quiz:
                title = instance.quiz.title
                description = f'Earned {points} points for high grade on quiz: {title}'
            else:
                title = "Unknown"
                description = f'Earned {points} points for high grade on {title}'

            # Create the PointTransaction entry
            PointTransaction.objects.create(
                user=instance.user,
                transaction_type='earn',
                points=points,
                description=description
            )

            # Update Ranking
            ranking, _ = Ranking.objects.get_or_create(user=instance.user)
            ranking.points += points
            ranking.save()

@receiver(post_save, sender=Challenge)
def handle_challenge_creation(sender, instance, created, **kwargs):
    if created:
        # Optionally, notify users about new challenges
        pass

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_ranking(sender, instance, created, **kwargs):
    if created:
        Ranking.objects.get_or_create(user=instance)
