import random
import pandas as pd
import numpy as np
import datetime
from django.core.exceptions import ValidationError
from .models import GeneratedCombination, LotteryDraw

def parse_excel_data(file_path):

    """Parse Excel data and import it into the database"""
    df = pd.read_excel(file_path)
    
    # Clear existing data
    LotteryDraw.objects.all().delete()
    
    # Import data from Excel file
    for _, row in df.iterrows():
        # Skip rows that don't have proper data format
        # Check if this is a valid lottery draw row
        if not isinstance(row.get('Draw Date'), (pd.Timestamp, datetime.datetime)) or \
           not isinstance(row.get('Winning Numbers'), str) or \
           not isinstance(row.get('Mega Ball'), (int, float, np.number)):
            continue
        
        try:
            LotteryDraw.objects.create(
                draw_date=row['Draw Date'],
                winning_numbers=row['Winning Numbers'],
                mega_ball=int(row['Mega Ball']),
                megaplier=int(row['Megaplier']) if pd.notna(row.get('Megaplier')) else None,
                estimated_jackpot=row['Estimated Jackpot'] if pd.notna(row.get('Estimated Jackpot')) else None,
                jackpot_winners=row['Jackpot Winners'] if pd.notna(row.get('Jackpot Winners')) else None
            )
        except (ValueError, TypeError, ValidationError):
            # Skip rows that cause validation errors
            continue

def get_all_drawn_combinations():
    """Get a set of all previously drawn combinations"""
    all_draws = LotteryDraw.objects.all()
    drawn_combinations = set()
    
    for draw in all_draws:
        drawn_combinations.add(draw.get_combination_key())
    
    return drawn_combinations

def has_been_drawn_before(main_numbers, mega_ball, drawn_combinations):
    """Check if a combination has been drawn before"""
    sorted_main_numbers = sorted(main_numbers)
    combination_key = f"{'-'.join(map(str, sorted_main_numbers))}-MB-{mega_ball}"
    return combination_key in drawn_combinations

def generate_random_combination():
    """Generate a random lottery combination"""
    # For Mega Millions: 5 numbers from 1-70, Mega Ball from 1-25
    main_numbers = set()
    while len(main_numbers) < 5:
        main_numbers.add(random.randint(1, 70))
    
    mega_ball = random.randint(1, 25)
    
    return {
        'main_numbers': sorted(list(main_numbers)),
        'mega_ball': mega_ball
    }

def generate_unique_combinations(count=10):
    """Generate unique lottery combinations that haven't been drawn before"""
    drawn_combinations = get_all_drawn_combinations()
    unique_combinations = []
    attempts = 0
    max_attempts = 1000000  # Safety limit
    
    while len(unique_combinations) < count and attempts < max_attempts:
        combination = generate_random_combination()
        attempts += 1
        
        if not has_been_drawn_before(
            combination['main_numbers'], 
            combination['mega_ball'], 
            drawn_combinations
        ):
            unique_combinations.append(combination)
    
    # Save generated combinations
    for combo in unique_combinations:
        GeneratedCombination.objects.create(
            main_numbers=', '.join(map(str, combo['main_numbers'])),
            mega_ball=combo['mega_ball']
        )
    
    return unique_combinations