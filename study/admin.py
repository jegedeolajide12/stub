from django.contrib import admin


from .models import Book, Chapter, Verse, UserReadingLog
# Register your models here.

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'testament']
    list_filter = ['testament']
    

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['book', 'number']
    list_filter = ['book']
    

@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'verse_number', 'text']
    

@admin.register(UserReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'read_at']
