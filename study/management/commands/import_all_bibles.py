import os
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Import all Bible translations from CSV files in a directory"

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='data',
            help='Directory containing Bible CSV files (default: data)'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            default='entire_*.csv',
            help='File pattern to match (default: entire_*.csv)'
        )

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        pattern = options['pattern']
        
        if not os.path.isdir(data_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {data_dir}"))
            return
        
        # Find all matching CSV files
        csv_files = sorted(glob.glob(os.path.join(data_dir, pattern)))
        
        if not csv_files:
            self.stdout.write(self.style.WARNING(f"No CSV files found matching {pattern} in {data_dir}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(csv_files)} Bible translation files"))
        
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Importing: {filename}")
            self.stdout.write('='*60)
            
            try:
                call_command('import_kjv', csv_file)
                self.stdout.write(self.style.SUCCESS(f"✓ {filename} imported successfully"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error importing {filename}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("All Bible translations imported!"))
        self.stdout.write(self.style.SUCCESS('='*60))
