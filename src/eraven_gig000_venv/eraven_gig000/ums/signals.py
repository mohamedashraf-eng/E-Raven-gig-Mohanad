# ums/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from cms.models import PointTransaction, Ranking

@receiver(post_save, sender=PointTransaction)
def update_user_points_and_level(sender, instance, created, **kwargs):
    if created:
        user = instance.user

        # Update ranking points if not tied directly to total points
        ranking, _ = Ranking.objects.get_or_create(user=user)
        
        # Example user level logic: 1 level per 100 total points
        user.level = (ranking.points // 100) + 1
        user.save(update_fields=['level'])

        # Save updated ranking, keeping points separate from user.total_points if needed
        ranking.save()
