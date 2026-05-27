from django.db import models

from django.utils import timezone
# Create your models here.


class Quest(models.Model):
    """A reading/study challenge."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    xp_reward = models.IntegerField(default=50)
    # verses to complete (many-to-many)
    verses = models.ManyToManyField('study.Verse', related_name='quests')
    days_to_complete = models.IntegerField(default=7)
    cover_image = models.ImageField(upload_to='quests/', blank=True)
    
    def __str__(self):
        return self.title

class UserQuestProgress(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='quest_progress')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.IntegerField(default=0)  # 0-100
    
    def complete(self):
        self.completed_at = timezone.now()
        self.progress_percent = 100
        self.user.profile.add_xp(self.quest.xp_reward)
        self.save()


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    bible_passage = models.ForeignKey('study.Verse', on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    xp_reward = models.IntegerField(default=30)
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    correct_answer = models.CharField(max_length=200)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    
class UserQuizAttempt(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Award XP based on score
        xp_earned = int(self.quiz.xp_reward * (self.score / 100))
        self.user.profile.add_xp(xp_earned)