# ums/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from cms.models import PointTransaction, Ranking
from cms.models import Enrollment 
from cms.models import UserProgress

@receiver(post_save, sender=PointTransaction)
def update_user_points_and_level(sender, instance, created, **kwargs):
    if created:
        user = instance.user

        # Update ranking points if not tied directly to total points
        ranking, _ = Ranking.objects.get_or_create(user=user)
        
        # Example user level logic: 1 level per 100 total points
        user.level = (ranking.points // 100) + 1
        user.save(update_fields=['level'])

        if user.total_points > ranking.points:
            ranking.points = user.total_points
            
        # Save updated ranking, keeping points separate from user.total_points if needed
        ranking.save()

@receiver(post_save, sender=Enrollment)
def create_or_update_user_progress(sender, instance, created, **kwargs):
    """
    Signal to create or update the user's progress when an enrollment is created.
    """
    if created:
        # Create a new UserProgress entry when enrollment is created
        UserProgress.objects.create(
            user=instance.user,
            course=instance.course,
            progress_percentage=0.0,  # Initial progress when enrollment is created
            completed=False  # Initially not completed
        )
    else:
        # If enrollment already exists, ensure there is a UserProgress entry
        user_progress, created = UserProgress.objects.get_or_create(
            user=instance.user,
            course=instance.course
        )
        if not created:
            # If user progress already exists, update it as needed
            user_progress.save()