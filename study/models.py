from django.db import models

# Create your models here.

class Book(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    testament = models.CharField(max_length=10, choices=[
        ('OT', 'Old Testament'),
        ('NT', 'New Testament')
    ])
    order = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.testament}"

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chapters")
    number = models.IntegerField()

    def __str__(self):
        return f"{self.book.name}- Chapter {self.number}"
    
class Verse(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="verses")
    verse_number = models.IntegerField()
    text = models.TextField()

    @property
    def reference(self):
        return f"{self.chapter.book.name}  {self.chapter.number}:{self.verse_number}"
    
    class Meta:
        unique_together = ['chapter', 'verse_number']
        ordering = ['chapter__book__order', 'chapter__number', 'verse_number']



class UserReadingLog(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name="reading_logs")
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'read_at'])]




class ReadingPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    days = models.IntegerField()  # total days
    cover_image = models.ImageField(upload_to='plans/', blank=True)
    # Many-to-many through PlanDay
    verses = models.ManyToManyField(Verse, through='PlanDay')
    
class PlanDay(models.Model):
    plan = models.ForeignKey(ReadingPlan, on_delete=models.CASCADE, related_name='plan_days')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    day_number = models.IntegerField()
    title = models.CharField(max_length=200, blank=True)
    
class UserPlanProgress(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='plan_progress')
    plan = models.ForeignKey(ReadingPlan, on_delete=models.CASCADE)
    current_day = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)