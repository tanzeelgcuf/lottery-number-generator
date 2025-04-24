import os
from django.core.management.base import BaseCommand
from django.conf import settings
from lottery_generator.utils import parse_excel_data

class Command(BaseCommand):
    help = 'Import lottery data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        file_path = options['mga2025.xlsx']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Importing data from {file_path}...'))
        parse_excel_data(file_path)
        self.stdout.write(self.style.SUCCESS('Data import complete!'))