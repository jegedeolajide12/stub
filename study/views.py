from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.utils import timezone
from django.db.models import Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required

from .models import (
    DailyDevotional, UserDevotionalProgress, Verse, Book, Chapter, 
    Translation, VerseTranslation, UserHighlight, UserBookmark, 
    UserVerseNote, CrossReference, VerseCommentary
)


class BibleReaderView(LoginRequiredMixin, TemplateView):
    """Main Bible reader page with book/chapter selection."""
    template_name = 'study/bible_reader.html'
    login_url = 'account_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get books organized by testament
        ot_books = Book.objects.filter(testament='OT').order_by('order')
        nt_books = Book.objects.filter(testament='NT').order_by('order')
        
        # Get selected book and chapter from URL or defaults
        book_id = self.kwargs.get('book_id')
        chapter_num = self.kwargs.get('chapter_num', 1)
        translation_id = self.kwargs.get('translation_id')
        
        # Get default translation
        default_translation = Translation.objects.filter(is_default=True).first()
        if not default_translation:
            default_translation = Translation.objects.first()
        
        if not translation_id and default_translation:
            translation_id = default_translation.id
        
        current_translation = Translation.objects.get(id=translation_id) if translation_id else default_translation
        
        context['ot_books'] = ot_books
        context['nt_books'] = nt_books
        context['translations'] = Translation.objects.all()
        context['current_translation'] = current_translation
        
        # Get verses if book and chapter specified
        if book_id and chapter_num:
            try:
                chapter = Chapter.objects.select_related('book').get(
                    book_id=book_id,
                    number=chapter_num
                )
                verses = chapter.verses.all().order_by('verse_number')
                
                # Enrich verses with user data
                if self.request.user.is_authenticated:
                    highlights = UserHighlight.objects.filter(
                        user=self.request.user,
                        verse__in=verses
                    ).values_list('verse_id', 'color')
                    highlight_dict = {v[0]: v[1] for v in highlights}
                    
                    bookmarks = UserBookmark.objects.filter(
                        user=self.request.user,
                        verse__in=verses
                    ).values_list('verse_id', flat=True)
                    bookmark_set = set(bookmarks)
                    
                    notes = UserVerseNote.objects.filter(
                        user=self.request.user,
                        verse__in=verses
                    ).values('verse_id', 'note')
                    note_dict = {n['verse_id']: n['note'] for n in notes}
                    
                    for verse in verses:
                        verse.user_highlight_color = highlight_dict.get(verse.id)
                        verse.is_bookmarked = verse.id in bookmark_set
                        verse.user_note = note_dict.get(verse.id)
                
                # Get verse translations
                verse_ids = [v.id for v in verses]
                translations_data = VerseTranslation.objects.filter(
                    verse_id__in=verse_ids,
                    translation=current_translation
                ).values('verse_id', 'text')
                translation_dict = {v['verse_id']: v['text'] for v in translations_data}
                
                for verse in verses:
                    verse.translation_text = translation_dict.get(verse.id, verse.text)
                
                context['current_chapter'] = chapter
                context['verses'] = verses
                context['chapter_count'] = chapter.book.chapters.count()
                
            except Chapter.DoesNotExist:
                context['current_chapter'] = None
                context['verses'] = []
        
        return context


class VerseDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single verse with commentary, cross-references."""
    model = Verse
    template_name = 'study/verse_detail.html'
    context_object_name = 'verse'
    pk_url_kwarg = 'verse_id'
    login_url = 'account_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        verse = self.get_object()
        
        # Get all translations of this verse
        context['verse_translations'] = VerseTranslation.objects.filter(
            verse=verse
        ).select_related('translation')
        
        # Get commentary
        context['commentary'] = VerseCommentary.objects.filter(verse=verse).first()
        
        # Get cross references
        context['cross_references'] = CrossReference.objects.filter(
            verse=verse
        ).select_related('referenced_verse__chapter__book')
        
        # Get user's highlight and bookmark
        if self.request.user.is_authenticated:
            context['user_highlight'] = UserHighlight.objects.filter(
                user=self.request.user,
                verse=verse
            ).first()
            context['user_bookmark'] = UserBookmark.objects.filter(
                user=self.request.user,
                verse=verse
            ).first()
            context['user_note'] = UserVerseNote.objects.filter(
                user=self.request.user,
                verse=verse
            ).first()
        
        return context


@login_required
@require_POST
def highlight_verse(request, verse_id):
    """Toggle highlight on a verse."""
    verse = get_object_or_404(Verse, id=verse_id)
    color = request.POST.get('color', 'yellow')
    
    highlight, created = UserHighlight.objects.get_or_create(
        user=request.user,
        verse=verse,
        defaults={'color': color}
    )
    
    if not created:
        highlight.color = color
        highlight.save()
    
    return JsonResponse({
        'success': True,
        'highlighted': True,
        'color': color
    })


@login_required
@require_POST
def remove_highlight(request, verse_id):
    """Remove highlight from verse."""
    UserHighlight.objects.filter(
        user=request.user,
        verse_id=verse_id
    ).delete()
    
    return JsonResponse({'success': True, 'highlighted': False})


@login_required
@require_POST
def bookmark_verse(request, verse_id):
    """Bookmark a verse."""
    verse = get_object_or_404(Verse, id=verse_id)
    label = request.POST.get('label', '')
    
    bookmark, created = UserBookmark.objects.get_or_create(
        user=request.user,
        verse=verse,
        defaults={'label': label}
    )
    
    if not created:
        bookmark.label = label
        bookmark.save()
    
    return JsonResponse({
        'success': True,
        'bookmarked': True,
        'label': label
    })


@login_required
@require_POST
def remove_bookmark(request, verse_id):
    """Remove bookmark from verse."""
    UserBookmark.objects.filter(
        user=request.user,
        verse_id=verse_id
    ).delete()
    
    return JsonResponse({'success': True, 'bookmarked': False})


@login_required
@require_POST
def save_verse_note(request, verse_id):
    """Save or update a note on a verse."""
    verse = get_object_or_404(Verse, id=verse_id)
    note = request.POST.get('note', '')
    
    verse_note, created = UserVerseNote.objects.update_or_create(
        user=request.user,
        verse=verse,
        defaults={'note': note}
    )
    
    return JsonResponse({
        'success': True,
        'note_saved': True,
        'note': verse_note.note
    })


@login_required
def delete_verse_note(request, verse_id):
    """Delete a note on a verse."""
    UserVerseNote.objects.filter(
        user=request.user,
        verse_id=verse_id
    ).delete()
    
    return JsonResponse({'success': True, 'note_deleted': True})


# Keep existing devotional views
class DevotionalListView(LoginRequiredMixin, TemplateView):
    """Display today's devotional and list of recent devotionals."""
    template_name = 'study/devotionals.html'
    login_url = 'account_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        today_devotional = DailyDevotional.objects.filter(
            published_date=today
        ).first()
        
        if not today_devotional:
            today_devotional = DailyDevotional.objects.filter(
                published_date__lte=today
            ).first()
        
        fourteen_days_ago = today - timezone.timedelta(days=14)
        recent_devotionals = DailyDevotional.objects.filter(
            published_date__gte=fourteen_days_ago,
            published_date__lte=today
        ).order_by('-published_date')
        
        if self.request.user.is_authenticated:
            user_progress = UserDevotionalProgress.objects.filter(
                user=self.request.user
            ).values_list('devotional_id', flat=True)
            
            for devotional in recent_devotionals:
                devotional.user_completed = devotional.id in user_progress
                if today_devotional and devotional.id == today_devotional.id:
                    devotional.is_today = True
        
        context['today_devotional'] = today_devotional
        context['recent_devotionals'] = recent_devotionals
        context['total_read'] = UserDevotionalProgress.objects.filter(
            user=self.request.user
        ).count() if self.request.user.is_authenticated else 0
        
        return context


class DevotionalDetailView(LoginRequiredMixin, DetailView):
    """Display a single devotional with full details."""
    model = DailyDevotional
    template_name = 'study/devotional_detail.html'
    context_object_name = 'devotional'
    slug_field = 'published_date'
    slug_url_kwarg = 'date'
    login_url = 'account_login'
    
    def get_object(self, queryset=None):
        date_str = self.kwargs.get('date')
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            return DailyDevotional.objects.get(published_date=date_obj)
        except (ValueError, DailyDevotional.DoesNotExist):
            raise Http404("Devotional not found")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        devotional = self.get_object()
        
        if self.request.user.is_authenticated:
            progress, created = UserDevotionalProgress.objects.get_or_create(
                user=self.request.user,
                devotional=devotional,
                defaults={'completed': True}
            )
            
            devotional.views += 1
            devotional.save()
            
            context['user_progress'] = progress
        
        context['next_devotional'] = DailyDevotional.objects.filter(
            published_date__gt=devotional.published_date
        ).order_by('published_date').first()
        
        context['prev_devotional'] = DailyDevotional.objects.filter(
            published_date__lt=devotional.published_date
        ).order_by('-published_date').first()
        
        return context


@login_required
@require_http_methods(["POST"])
def mark_devotional_complete(request, devotional_id):
    """Mark a devotional as completed (AJAX endpoint)."""
    devotional = get_object_or_404(DailyDevotional, id=devotional_id)
    
    progress, created = UserDevotionalProgress.objects.get_or_create(
        user=request.user,
        devotional=devotional,
        defaults={'completed': True}
    )
    
    if not created:
        progress.completed = True
        progress.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Devotional marked as complete!',
        'completed': progress.completed
    })


@login_required
@require_http_methods(["POST"])
def save_reflection(request, devotional_id):
    """Save user's reflection note on a devotional."""
    devotional = get_object_or_404(DailyDevotional, id=devotional_id)
    reflection_note = request.POST.get('reflection_note', '')
    
    progress, created = UserDevotionalProgress.objects.get_or_create(
        user=request.user,
        devotional=devotional
    )
    
    progress.reflection_note = reflection_note
    progress.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Reflection saved successfully!'
    })
