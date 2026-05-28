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


class DailyDevotional(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()  # Main devotional content
    theme = models.CharField(max_length=100, blank=True)
    key_verse = models.ForeignKey(Verse, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.CharField(max_length=100, blank=True)
    reflection_prompt = models.TextField(blank=True)  # Reflection question
    prayer_request = models.TextField(blank=True)
    published_date = models.DateField(unique=True, db_index=True)  # One devotional per day
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = 'Daily Devotionals'
    
    def __str__(self):
        return f"{self.title} - {self.published_date}"
    
    @property
    def reference(self):
        if self.key_verse:
            return self.key_verse.reference
        return None


class UserDevotionalProgress(models.Model):
    """Track which devotionals users have interacted with."""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='devotional_progress')
    devotional = models.ForeignKey(DailyDevotional, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    read_at = models.DateTimeField(auto_now_add=True)
    reflection_note = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('user', 'devotional')
        ordering = ['-read_at']


class Translation(models.Model):
    """Different Bible translations."""
    name = models.CharField(max_length=100, unique=True)  # KJV, NIV, NKJV, ESV, etc.
    abbreviation = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class VerseTranslation(models.Model):
    """Verse text in different translations."""
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='translations')
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE)
    text = models.TextField()
    
    class Meta:
        unique_together = ('verse', 'translation')
    
    def __str__(self):
        return f"{self.verse.reference} - {self.translation.abbreviation}"


class UserHighlight(models.Model):
    """User-highlighted verses with color coding."""
    COLOR_CHOICES = [
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('purple', 'Purple'),
    ]
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='highlights')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-created_at']


class UserBookmark(models.Model):
    """Bookmarked verses/chapters."""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='bookmarks')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, blank=True)  # "To memorize", "Important", etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-created_at']


class UserVerseNote(models.Model):
    """Personal notes on verses."""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='verse_notes')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-updated_at']


class CrossReference(models.Model):
    """Related verses that reference each other."""
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='cross_references')
    referenced_verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='referenced_by')
    note = models.CharField(max_length=200, blank=True)  # e.g., "See also", "Fulfills prophecy"
    
    def __str__(self):
        return f"{self.verse.reference} → {self.referenced_verse.reference}"


class VerseCommentary(models.Model):
    """AI-generated or curated commentary on verses."""
    verse = models.OneToOneField(Verse, on_delete=models.CASCADE, related_name='commentary')
    summary = models.TextField()  # Short explanation
    cultural_context = models.TextField(blank=True)
    theological_meaning = models.TextField(blank=True)
    practical_application = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Commentary: {self.verse.reference}"
    
    class Meta:
        verbose_name_plural = 'Verse Commentaries'