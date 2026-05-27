from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    preferred_translation = models.CharField(max_length=10, choices=[
        ('kjv', 'KJV'),
        ('niv', 'NIV'),
        ('nkjv', 'NKJV'),
    ], default='niv')


    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_read_date = models.DateField(blank=True, null=True)

    level = models.IntegerField(default=1)
    xp_to_next_level = models.IntegerField(default=100)

    total_verses_read = models.IntegerField(default=0)
    total_insights_saved = models.IntegerField(default=0)
    total_correct_quiz = models.IntegerField(default=0)

    daily_reminder = models.BooleanField(default=False)
    reminder_time = models.TimeField(blank=True, null=True)
    weekly_review = models.BooleanField(default=False)

    def update_streak(self, date=None):
        today = date or timezone.now().date()
        if self.last_read_date == today:
            return
        if self.last_read_date == today - timezone.timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        self.last_read_date = today
        self.save()

    def add_xp(self, xp):
        self.user.total_xp += xp
        while self.user.total_xp >= self.xp_to_next_level:
            self.user.total_xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        self.user.save()
        self.save()