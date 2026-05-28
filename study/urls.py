from django.urls import path
from .views import (
    # Bible Reader
    BibleReaderView,
    VerseDetailView,
    highlight_verse,
    remove_highlight,
    bookmark_verse,
    remove_bookmark,
    save_verse_note,
    delete_verse_note,
    # Devotionals
    DevotionalListView, 
    DevotionalDetailView,
    mark_devotional_complete,
    save_reflection
)

app_name = "study"

urlpatterns = [
    # Bible Reader
    path("bible/", BibleReaderView.as_view(), name="bible_reader"),
    path("bible/<int:book_id>/", BibleReaderView.as_view(), name="bible_book"),
    path("bible/<int:book_id>/<int:chapter_num>/", BibleReaderView.as_view(), name="bible_chapter"),
    path("bible/<int:book_id>/<int:chapter_num>/<int:translation_id>/", BibleReaderView.as_view(), name="bible_chapter_translation"),
    path("verse/<int:verse_id>/", VerseDetailView.as_view(), name="verse_detail"),
    path("verse/<int:verse_id>/highlight/", highlight_verse, name="highlight_verse"),
    path("verse/<int:verse_id>/highlight/remove/", remove_highlight, name="remove_highlight"),
    path("verse/<int:verse_id>/bookmark/", bookmark_verse, name="bookmark_verse"),
    path("verse/<int:verse_id>/bookmark/remove/", remove_bookmark, name="remove_bookmark"),
    path("verse/<int:verse_id>/note/", save_verse_note, name="save_verse_note"),
    path("verse/<int:verse_id>/note/delete/", delete_verse_note, name="delete_verse_note"),
    
    # Devotionals
    path("devotionals/", DevotionalListView.as_view(), name="devotionals"),
    path("devotionals/<str:date>/", DevotionalDetailView.as_view(), name="devotional_detail"),
    path("devotionals/<int:devotional_id>/complete/", mark_devotional_complete, name="mark_complete"),
    path("devotionals/<int:devotional_id>/save-reflection/", save_reflection, name="save_reflection"),
]