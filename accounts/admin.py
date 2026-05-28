from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fields = ('current_streak', 'longest_streak', 'last_read_date', 'level', 
              'xp_to_next_level', 'total_verses_read', 'total_insights_saved', 
              'total_correct_quiz', 'daily_reminder', 'reminder_time', 'weekly_review')
    readonly_fields = ('current_streak', 'longest_streak', 'last_read_date')
    extra = 0


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "level",
        "total_xp",
        "is_staff",
        "is_active",
    ]
    list_filter = ['is_staff', 'is_active', 'level']
    search_fields = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'bio', 'avatar', 'preferred_translation')}),
        ('Progression', {'fields': ('total_xp', 'level')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [UserProfileInline]


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'current_streak', 'total_verses_read', 'daily_reminder']
    list_filter = ['level', 'current_streak', 'daily_reminder', 'weekly_review']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_read_date', 'current_streak', 'longest_streak']
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Streaks', {'fields': ('current_streak', 'longest_streak', 'last_read_date')}),
        ('Progression', {'fields': ('level', 'xp_to_next_level')}),
        ('Stats', {'fields': ('total_verses_read', 'total_insights_saved', 'total_correct_quiz')}),
        ('Notifications', {'fields': ('daily_reminder', 'reminder_time', 'weekly_review')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
