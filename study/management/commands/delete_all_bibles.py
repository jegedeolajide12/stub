from django.core.management.base import BaseCommand
from django.db import connection
from study.models import Book, Chapter, Verse, Translation, VerseTranslation

class Command(BaseCommand):
    help = "Delete all imported Bible data (books, chapters, verses, translations)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting'
        )
        parser.add_argument(
            '--keep-books',
            action='store_true',
            help='Keep Book records, only delete verses and translations'
        )

    def delete_in_batches(self, queryset, batch_size=1000, model_name="records"):
        """Delete records in batches to avoid 'too many SQL variables' error"""
        total = queryset.count()
        deleted = 0
        
        while deleted < total:
            batch = list(queryset[:batch_size].values_list('id', flat=True))
            if not batch:
                break
            queryset.model.objects.filter(id__in=batch).delete()
            deleted += len(batch)
            progress = min(deleted, total)
            self.stdout.write(f"\r  Deleting {model_name}... {progress}/{total}", ending='')
        
        self.stdout.write(self.style.SUCCESS(f"\r  Deleting {model_name}... ✓                    "))

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING("⚠️  WARNING: This will DELETE all Bible data!"))
            self.stdout.write("This includes:")
            self.stdout.write("  - All VerseTranslation records")
            self.stdout.write("  - All Verse records")
            self.stdout.write("  - All Chapter records")
            self.stdout.write("  - All Book records")
            self.stdout.write("  - All Translation records\n")
            
            confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
            if confirm != 'yes':
                self.stdout.write(self.style.SUCCESS("Deletion cancelled."))
                return

        try:
            self.stdout.write("Deleting Bible data...\n")
            
            # Count current records
            verse_trans_count = VerseTranslation.objects.count()
            verse_count = Verse.objects.count()
            chapter_count = Chapter.objects.count()
            book_count = Book.objects.count()
            translation_count = Translation.objects.count()
            
            self.stdout.write(f"VerseTranslation records: {verse_trans_count}")
            self.stdout.write(f"Verse records: {verse_count}")
            self.stdout.write(f"Chapter records: {chapter_count}")
            self.stdout.write(f"Book records: {book_count}")
            self.stdout.write(f"Translation records: {translation_count}\n")
            
            # Delete in order (respect foreign keys)
            # Use batch deletion to avoid "too many SQL variables" error
            self.delete_in_batches(
                VerseTranslation.objects.all(),
                batch_size=1000,
                model_name="VerseTranslation records"
            )
            
            self.delete_in_batches(
                Verse.objects.all(),
                batch_size=1000,
                model_name="Verse records"
            )
            
            self.delete_in_batches(
                Chapter.objects.all(),
                batch_size=1000,
                model_name="Chapter records"
            )
            
            if not options['keep_books']:
                self.delete_in_batches(
                    Book.objects.all(),
                    batch_size=1000,
                    model_name="Book records"
                )
            
            self.delete_in_batches(
                Translation.objects.all(),
                batch_size=1000,
                model_name="Translation records"
            )
            
            self.stdout.write(self.style.SUCCESS("\n✓ All Bible data deleted successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during deletion: {str(e)}"))
