import csv
import os
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from study.models import Book, Chapter, Verse, Translation, VerseTranslation

# List of Old Testament books (order based on KJV)
OT_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi"
]

# Translation full names mapping
TRANSLATION_NAMES = {
    'kjv': 'King James Version',
    'niv': 'New International Version',
    'nkjv': 'New King James Version',
    'esv': 'English Standard Version',
    'nasb1995': 'New American Standard Bible 1995',
    'nlt': 'New Living Translation',
    'msg': 'The Message',
    'asv': 'American Standard Version',
    'csb': 'Christian Standard Bible',
    'bsb': 'Berean Standard Bible',
    'lsb': 'LBSE Bible',
    'erv': 'Easy-to-Read Version',
    'easy': 'Easy English Bible',
    'gw': 'God\'s Word',
    'hcsb': 'Holman Christian Standard Bible',
    'nirv': 'New International Reader\'s Version',
    'nrsv': 'New Revised Standard Version',
    'rsv': 'Revised Standard Version',
    'darby': 'Darby Bible',
    'leb': 'Lexham English Bible',
    'amp': 'Amplified Bible',
    'ampc': 'Amplified Bible Classic',
    'cev': 'Contemporary English Version',
    'cevuk': 'Contemporary English Version UK',
    'cjb': 'Complete Jewish Bible',
    'fbv': 'Forsyth Bible Version',
    'gnbuk': 'Good News Bible UK',
    'gnt': 'Good News Translation',
    'gnv': 'Geneva Bible',
    'icb': 'International Children\'s Bible',
    'mev': 'Modern English Version',
    'nmv': 'New Matthew Bible',
    'nivuk': 'New International Version UK',
    'rvr1960': 'Reina Valera 1960',
    'tojb2011': 'The Orthodox Jewish Bible 2011',
}

def get_testament(book_name):
    return "OT" if book_name in OT_BOOKS else "NT"

def get_abbreviation(book_name):
    """Simple abbreviation: first 3 letters uppercase, handle numbers."""
    # Custom overrides for common cases
    overrides = {
        "1 Samuel": "1SA",
        "2 Samuel": "2SA",
        "1 Kings": "1KI",
        "2 Kings": "2KI",
        "1 Chronicles": "1CH",
        "2 Chronicles": "2CH",
        "Song of Solomon": "SON",
        "Psalms": "PSA",
    }
    if book_name in overrides:
        return overrides[book_name]
    # For books like "1 John", "2 John", etc.
    if book_name[0].isdigit():
        parts = book_name.split()
        num = parts[0]
        name = parts[1][:3].upper()
        return f"{num}{name}"
    return book_name[:3].upper()

def extract_translation_from_filename(csv_path):
    """Extract translation code from filename like entire_kjv.csv -> KJV"""
    filename = os.path.basename(csv_path)
    match = re.search(r'entire_(\w+)\.csv', filename)
    if match:
        code = match.group(1).upper()
        return code
    return None

class Command(BaseCommand):
    help = "Import Bible verses from CSV into the database"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to csv_file')
        parser.add_argument(
            '--translation',
            type=str,
            help='Translation abbreviation (e.g., KJV, NIV). If not provided, extracted from filename.'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed logging for debugging'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        translation_abbr = options.get('translation')
        verbose = options.get('verbose', False)
        
        # Try to extract translation from filename if not provided
        if not translation_abbr:
            translation_abbr = extract_translation_from_filename(csv_path)
        
        if not translation_abbr:
            self.stdout.write(self.style.ERROR(
                "Could not determine translation. Please use --translation flag."
            ))
            return
        
        translation_abbr = translation_abbr.upper()
        translation_name = TRANSLATION_NAMES.get(translation_abbr.lower(), translation_abbr)
        
        self.stdout.write(f"Importing {translation_abbr} ({translation_name})...")
        
        # Get or create Translation
        translation, created = Translation.objects.get_or_create(
            abbreviation=translation_abbr,
            defaults={'name': translation_name, 'is_default': translation_abbr == 'KJV'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created translation: {translation.name}"))
        else:
            self.stdout.write(f"Using existing translation: {translation.name}")
        
        book_cache = {}   # name -> Book instance
        chapter_cache = {} # (book_id, chapter_num) -> Chapter instance
        verse_translations_to_create = []
        sample_count = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip the first line (0,1,2,3)
            next(reader, None)

            for row in reader:
                if len(row) < 4:
                    if verbose:
                        self.stdout.write(self.style.WARNING(f"Skipped incomplete row: {row}"))
                    continue
                book_name, chapter_str, verse_str, verse_text = row[:4]
                
                if verbose and sample_count < 3:
                    self.stdout.write(f"Sample row {sample_count}: book='{book_name}', ch={chapter_str}, v={verse_str}, text='{verse_text[:50]}...'")
                    sample_count += 1
                
                try:
                    chapter_num = int(chapter_str)
                    verse_num = int(verse_str)
                except ValueError:
                    if verbose:
                        self.stdout.write(self.style.WARNING(f"Invalid chapter/verse numbers: {chapter_str}/{verse_str}"))
                    continue

                # Get or create Book
                if book_name not in book_cache:
                    book, _ = Book.objects.get_or_create(
                        name=book_name,
                        defaults={
                            'abbreviation': get_abbreviation(book_name),
                            'testament': get_testament(book_name),
                            'order': len(book_cache) + 1   # order as first seen
                        }
                    )
                    book_cache[book_name] = book
                book = book_cache[book_name]

                # Get or create Chapter
                key = (book.id, chapter_num)
                if key not in chapter_cache:
                    chapter, _ = Chapter.objects.get_or_create(
                        book=book,
                        number=chapter_num
                    )
                    chapter_cache[key] = chapter
                chapter = chapter_cache[key]

                # Get or create Verse (without translation-specific text)
                verse, _ = Verse.objects.get_or_create(
                    chapter=chapter,
                    verse_number=verse_num
                )

                # Create VerseTranslation instance
                verse_translations_to_create.append(
                    VerseTranslation(
                        verse=verse,
                        translation=translation,
                        text=verse_text.strip()
                    )
                )

                # Bulk create in batches to avoid memory issues
                if len(verse_translations_to_create) >= 5000:
                    self._bulk_create_batch(verse_translations_to_create, verbose)
                    verse_translations_to_create = []

        # Final batch
        if verse_translations_to_create:
            self._bulk_create_batch(verse_translations_to_create, verbose)

        # Count verses imported for this translation
        verse_count = VerseTranslation.objects.filter(translation=translation).count()
        self.stdout.write(self.style.SUCCESS(
            f"\nImport completed. Books: {len(book_cache)}, "
            f"Verse translations for {translation_abbr}: {verse_count}"
        ))
    
    def _bulk_create_batch(self, batch, verbose=False):
        """Create a batch of VerseTranslation records with error handling."""
        try:
            created = VerseTranslation.objects.bulk_create(
                batch,
                batch_size=1000,
                ignore_conflicts=True
            )
            self.stdout.write(f'.({len(created)})', ending='')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError creating batch: {str(e)}"))
            # Skip the batch - don't try to save individually since transaction is broken
            if verbose:
                self.stdout.write(self.style.WARNING(f"Skipped {len(batch)} records due to error"))