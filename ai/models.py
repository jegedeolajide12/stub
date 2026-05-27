from django.db import models


# Create your models here.

class Insight(models.Model):
    verse = models.ForeignKey('study.Verse', on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=20, choices=[
        ('cultural', 'Cultural Context'),
        ('word_study', 'Greek/Hebrew Word Study'),
        ('application', 'Life Application'),
        ('theological', 'Theological Note')
    ])
    content = models.TextField()
    created_by_ai = models.BooleanField(default=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.verse.refernce} - {self.insight_type}"

class SavedInsight(models.Model):
    """Users can save AI insights to their library."""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='saved_insights')
    insight = models.ForeignKey(Insight, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)  # optional personal note
    
    class Meta:
        unique_together = ('user', 'insight')

class UserNote(models.Model):
    """Personal notes on verses (Notion-like)."""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notes')
    verse = models.ForeignKey('study.Verse', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.verse.reference}"
