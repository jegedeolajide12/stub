from django.contrib import admin
from .models import Insight, SavedInsight, UserNote


class InsightAdmin(admin.ModelAdmin):
    list_display = ['verse', 'insight_type', 'upvotes', 'downvotes', 'created_by_ai', 'created_at']
    list_filter = ['insight_type', 'created_by_ai', 'created_at']
    search_fields = ['verse__text', 'content', 'verse__reference']
    readonly_fields = ['created_at', 'upvotes', 'downvotes']
    fieldsets = (
        ('Verse Info', {'fields': ('verse',)}),
        ('Insight Details', {'fields': ('insight_type', 'content')}),
        ('Engagement', {'fields': ('upvotes', 'downvotes')}),
        ('Metadata', {'fields': ('created_by_ai', 'created_at')}),
    )
    ordering = ['-created_at']


class SavedInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight', 'saved_at']
    list_filter = ['saved_at', 'user']
    search_fields = ['user__username', 'insight__content', 'note']
    readonly_fields = ['saved_at']
    fieldsets = (
        ('User & Insight', {'fields': ('user', 'insight')}),
        ('Personal Note', {'fields': ('note',)}),
        ('Metadata', {'fields': ('saved_at',)}),
    )
    ordering = ['-saved_at']


class UserNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['user__username', 'verse__text', 'title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User & Verse', {'fields': ('user', 'verse')}),
        ('Note Content', {'fields': ('title', 'content')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    ordering = ['-updated_at']


admin.site.register(Insight, InsightAdmin)
admin.site.register(SavedInsight, SavedInsightAdmin)
admin.site.register(UserNote, UserNoteAdmin)
