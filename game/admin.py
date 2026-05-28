from django.contrib import admin
from .models import Quest, UserQuestProgress, Quiz, Question, UserQuizAttempt


class QuestionInline(admin.TabularInline):
    model = Question
    fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    extra = 1


class QuestAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'xp_reward', 'days_to_complete']
    list_filter = ['difficulty', 'days_to_complete']
    search_fields = ['title', 'description']
    filter_horizontal = ['verses']
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description')}),
        ('Challenge Details', {'fields': ('difficulty', 'xp_reward', 'days_to_complete')}),
        ('Content', {'fields': ('verses', 'cover_image')}),
    )
    ordering = ['-id']


class UserQuestProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'quest', 'progress_percent', 'started_at', 'completed_at']
    list_filter = ['quest', 'started_at', 'completed_at']
    search_fields = ['user__username', 'quest__title']
    readonly_fields = ['started_at', 'progress_percent']
    fieldsets = (
        ('User & Quest', {'fields': ('user', 'quest')}),
        ('Progress', {'fields': ('progress_percent',)}),
        ('Timeline', {'fields': ('started_at', 'completed_at')}),
    )
    ordering = ['-started_at']


class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'xp_reward', 'bible_passage']
    list_filter = ['difficulty']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Quiz Info', {'fields': ('title', 'description')}),
        ('Bible Reference', {'fields': ('bible_passage',)}),
        ('Settings', {'fields': ('difficulty', 'xp_reward')}),
    )
    inlines = [QuestionInline]
    ordering = ['-id']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text', 'correct_answer']
    list_filter = ['quiz']
    search_fields = ['quiz__title', 'text', 'correct_answer']
    fieldsets = (
        ('Question', {'fields': ('quiz', 'text')}),
        ('Options', {'fields': ('option_a', 'option_b', 'option_c', 'option_d')}),
        ('Answer', {'fields': ('correct_answer',)}),
    )
    ordering = ['quiz', '-id']


class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'completed_at']
    list_filter = ['completed_at', 'quiz', 'score']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['completed_at', 'score']
    fieldsets = (
        ('User & Quiz', {'fields': ('user', 'quiz')}),
        ('Performance', {'fields': ('score',)}),
        ('Timeline', {'fields': ('completed_at',)}),
    )
    ordering = ['-completed_at']


admin.site.register(Quest, QuestAdmin)
admin.site.register(UserQuestProgress, UserQuestProgressAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserQuizAttempt, UserQuizAttemptAdmin)
