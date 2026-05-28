from django.contrib import admin
from .models import (
    Book, Chapter, Verse, UserReadingLog, ReadingPlan, 
    PlanDay, UserPlanProgress, DailyDevotional, UserDevotionalProgress,
    Translation, VerseTranslation, UserHighlight, UserBookmark, 
    UserVerseNote, CrossReference, VerseCommentary
)


class ChapterInline(admin.TabularInline):
    model = Chapter
    fields = ['number']
    extra = 1


class VerseInline(admin.TabularInline):
    model = Verse
    fields = ['verse_number', 'text']
    extra = 1


class PlanDayInline(admin.TabularInline):
    model = PlanDay
    fields = ['day_number', 'verse', 'title']
    extra = 1


class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'testament', 'order']
    list_filter = ['testament']
    search_fields = ['name', 'abbreviation']
    fieldsets = (
        ('Book Info', {'fields': ('name', 'abbreviation')}),
        ('Scripture Position', {'fields': ('testament', 'order')}),
    )
    inlines = [ChapterInline]
    ordering = ['order']


class ChapterAdmin(admin.ModelAdmin):
    list_display = ['book', 'number']
    list_filter = ['book']
    search_fields = ['book__name']
    fieldsets = (
        ('Chapter Info', {'fields': ('book', 'number')}),
    )
    inlines = [VerseInline]
    ordering = ['book__order', 'number']


class VerseAdmin(admin.ModelAdmin):
    list_display = ['reference', 'chapter', 'verse_number']
    list_filter = ['chapter__book', 'chapter']
    search_fields = ['text', 'chapter__book__name']
    readonly_fields = ['reference']
    fieldsets = (
        ('Verse Location', {'fields': ('chapter', 'verse_number')}),
        ('Content', {'fields': ('text',)}),
        ('Reference', {'fields': ('reference',)}),
    )
    ordering = ['chapter__book__order', 'chapter__number', 'verse_number']


class UserReadingLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'read_at']
    list_filter = ['read_at', 'user']
    search_fields = ['user__username', 'verse__text', 'verse__chapter__book__name']
    readonly_fields = ['read_at']
    fieldsets = (
        ('User & Verse', {'fields': ('user', 'verse')}),
        ('Timestamp', {'fields': ('read_at',)}),
    )
    ordering = ['-read_at']


class ReadingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'days']
    list_filter = ['days']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Plan Info', {'fields': ('name', 'description')}),
        ('Details', {'fields': ('days', 'cover_image')}),
    )
    inlines = [PlanDayInline]
    ordering = ['-id']


class PlanDayAdmin(admin.ModelAdmin):
    list_display = ['plan', 'day_number', 'verse', 'title']
    list_filter = ['plan', 'day_number']
    search_fields = ['plan__name', 'title', 'verse__text']
    fieldsets = (
        ('Plan Assignment', {'fields': ('plan', 'day_number')}),
        ('Verse & Title', {'fields': ('verse', 'title')}),
    )
    ordering = ['plan', 'day_number']


class UserPlanProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'current_day', 'started_at', 'completed_at']
    list_filter = ['plan', 'started_at', 'completed_at']
    search_fields = ['user__username', 'plan__name']
    readonly_fields = ['started_at']
    fieldsets = (
        ('User & Plan', {'fields': ('user', 'plan')}),
        ('Progress', {'fields': ('current_day',)}),
        ('Timeline', {'fields': ('started_at', 'completed_at')}),
    )
    ordering = ['-started_at']


class DailyDevotionalAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_date', 'theme', 'author', 'featured', 'views']
    list_filter = ['published_date', 'featured', 'theme']
    search_fields = ['title', 'content', 'author', 'theme']
    readonly_fields = ['views', 'created_at', 'updated_at']
    fieldsets = (
        ('Devotional Info', {'fields': ('title', 'theme', 'author')}),
        ('Content', {'fields': ('content', 'key_verse', 'reference')}),
        ('Reflection & Prayer', {'fields': ('reflection_prompt', 'prayer_request')}),
        ('Publishing', {'fields': ('published_date', 'featured')}),
        ('Engagement', {'fields': ('views',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    date_hierarchy = 'published_date'
    ordering = ['-published_date']
    
    def reference(self, obj):
        return obj.reference
    reference.short_description = 'Verse Reference'


class UserDevotionalProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'devotional', 'completed', 'read_at']
    list_filter = ['completed', 'read_at', 'devotional']
    search_fields = ['user__username', 'devotional__title', 'reflection_note']
    readonly_fields = ['read_at']
    fieldsets = (
        ('User & Devotional', {'fields': ('user', 'devotional')}),
        ('Progress', {'fields': ('completed',)}),
        ('Reflection', {'fields': ('reflection_note',)}),
        ('Timestamp', {'fields': ('read_at',)}),
    )
    ordering = ['-read_at']


admin.site.register(Book, BookAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Verse, VerseAdmin)
admin.site.register(UserReadingLog, UserReadingLogAdmin)
admin.site.register(ReadingPlan, ReadingPlanAdmin)
admin.site.register(PlanDay, PlanDayAdmin)
admin.site.register(UserPlanProgress, UserPlanProgressAdmin)
admin.site.register(DailyDevotional, DailyDevotionalAdmin)
admin.site.register(UserDevotionalProgress, UserDevotionalProgressAdmin)


# ========== BIBLE READER ADMIN ==========

class VerseTranslationInline(admin.TabularInline):
    model = VerseTranslation
    fields = ['translation', 'text']
    extra = 1


class CrossReferenceInline(admin.TabularInline):
    model = CrossReference
    fields = ['referenced_verse', 'note']
    fk_name = 'verse'
    extra = 1


class TranslationAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_default']
    list_filter = ['is_default']
    search_fields = ['name', 'abbreviation']
    fieldsets = (
        ('Translation Info', {'fields': ('name', 'abbreviation')}),
        ('Settings', {'fields': ('is_default',)}),
        ('Description', {'fields': ('description',)}),
    )


class VerseTranslationAdmin(admin.ModelAdmin):
    list_display = ['verse', 'translation', 'text']
    list_filter = ['translation', 'verse__chapter__book']
    search_fields = ['verse__text', 'text']
    fieldsets = (
        ('Verse & Translation', {'fields': ('verse', 'translation')}),
        ('Text', {'fields': ('text',)}),
    )


class UserHighlightAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'color', 'created_at']
    list_filter = ['color', 'created_at', 'user']
    search_fields = ['user__username', 'verse__text']
    readonly_fields = ['created_at']
    fieldsets = (
        ('User & Verse', {'fields': ('user', 'verse')}),
        ('Highlight', {'fields': ('color',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    ordering = ['-created_at']


class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'label', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'verse__text', 'label']
    readonly_fields = ['created_at']
    fieldsets = (
        ('User & Verse', {'fields': ('user', 'verse')}),
        ('Bookmark', {'fields': ('label',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    ordering = ['-created_at']


class UserVerseNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['user__username', 'verse__text', 'note']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User & Verse', {'fields': ('user', 'verse')}),
        ('Note', {'fields': ('note',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    ordering = ['-updated_at']


class CrossReferenceAdmin(admin.ModelAdmin):
    list_display = ['verse', 'referenced_verse', 'note']
    list_filter = ['verse__chapter__book']
    search_fields = ['verse__text', 'referenced_verse__text', 'note']
    fieldsets = (
        ('Verses', {'fields': ('verse', 'referenced_verse')}),
        ('Note', {'fields': ('note',)}),
    )


class VerseCommentaryAdmin(admin.ModelAdmin):
    list_display = ['verse', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['verse__text', 'summary', 'cultural_context']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Verse', {'fields': ('verse',)}),
        ('Commentary', {
            'fields': ('summary', 'cultural_context', 'theological_meaning', 'practical_application')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    ordering = ['-created_at']


admin.site.register(Translation, TranslationAdmin)
admin.site.register(VerseTranslation, VerseTranslationAdmin)
admin.site.register(UserHighlight, UserHighlightAdmin)
admin.site.register(UserBookmark, UserBookmarkAdmin)
admin.site.register(UserVerseNote, UserVerseNoteAdmin)
admin.site.register(CrossReference, CrossReferenceAdmin)
admin.site.register(VerseCommentary, VerseCommentaryAdmin)


