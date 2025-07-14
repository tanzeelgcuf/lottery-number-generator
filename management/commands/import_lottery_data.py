import os
from django.core.management.base import BaseCommand
from django.conf import settings
from lottery_generator.utils import parse_excel_data

class Command(BaseCommand):
    help = 'Import lottery data from Excel file with enhanced features'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')
        parser.add_argument(
            '--game-type',
            type=str,
            choices=['mega_millions', 'powerball'],
            default='mega_millions',
            help='Type of lottery game (default: mega_millions)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data for this game type before importing'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        game_type = options['game_type']
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Importing {game_type} data from {file_path}...'
            )
        )
        
        try:
            # Import the data
            parse_excel_data(file_path, game_type)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {game_type} data!'
                )
            )
            
            # Show import statistics
            from lottery_generator.models import LotteryDraw
            count = LotteryDraw.objects.filter(game_type=game_type).count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Total {game_type} draws in database: {count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )
            
        self.stdout.write(
            self.style.SUCCESS('Data import process complete!')
        )