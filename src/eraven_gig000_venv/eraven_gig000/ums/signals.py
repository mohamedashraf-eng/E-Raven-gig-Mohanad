# ums/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from cms.models import PointTransaction, Ranking

@receiver(post_save, sender=PointTransaction)
def update_user_points_and_level(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        if instance.transaction_type == 'earn':
            user.total_points += instance.points
        elif instance.transaction_type == 'spend':
            user.total_points -= instance.points
            if user.total_points < 0:
                user.total_points = 0  # Prevent negative points

        # Update user level based on total points (example logic)
        user.level = (user.total_points // 100) + 1  # Each 100 points = new level

        user.save()

        # Update or create ranking
        ranking, created = Ranking.objects.get_or_create(user=user)
        # 
        # User points will be separated from ranking points (Total points earned by user)
        # ranking.points = user.total_points
        ranking.save()
