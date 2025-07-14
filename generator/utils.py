import random
import pandas as pd
import numpy as np
import datetime
import requests
import csv
import io
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import GeneratedCombination, LotteryDraw, SavedCombination, CombinationCheck

def parse_excel_data(file_path, game_type='mega_millions'):
    """Parse Excel data and import it into the database"""
    df = pd.read_excel(file_path)
    
    # Clear existing data for this game type
    LotteryDraw.objects.filter(game_type=game_type).delete()
    
    # Import data from Excel file
    for _, row in df.iterrows():
        # Skip rows that don't have proper data format
        if not isinstance(row.get('Draw Date'), (pd.Timestamp, datetime.datetime)) or \
           not isinstance(row.get('Winning Numbers'), str) or \
           not isinstance(row.get('Mega Ball'), (int, float, np.number)):
            continue
        
        try:
            LotteryDraw.objects.create(
                game_type=game_type,
                draw_date=row['Draw Date'],
                winning_numbers=row['Winning Numbers'],
                mega_ball=int(row['Mega Ball']),
                megaplier=int(row['Megaplier']) if pd.notna(row.get('Megaplier')) else None,
                estimated_jackpot=row['Estimated Jackpot'] if pd.notna(row.get('Estimated Jackpot')) else None,
                jackpot_winners=row['Jackpot Winners'] if pd.notna(row.get('Jackpot Winners')) else None
            )
        except (ValueError, TypeError, ValidationError):
            continue

def get_all_drawn_combinations(game_type='mega_millions'):
    """Get a set of all previously drawn combinations for a specific game"""
    all_draws = LotteryDraw.objects.filter(game_type=game_type)
    drawn_combinations = set()
    
    for draw in all_draws:
        drawn_combinations.add(draw.get_combination_key())
    
    return drawn_combinations

def has_been_drawn_before(main_numbers, mega_ball, drawn_combinations):
    """Check if a combination has been drawn before"""
    sorted_main_numbers = sorted(main_numbers)
    combination_key = f"{'-'.join(map(str, sorted_main_numbers))}-MB-{mega_ball}"
    return combination_key in drawn_combinations

def generate_random_combination(game_type='mega_millions'):
    """Generate a random lottery combination based on game type"""
    if game_type == 'mega_millions':
        # Mega Millions: 5 numbers from 1-70, Mega Ball from 1-25
        main_range = (1, 70)
        mega_range = (1, 25)
        main_count = 5
    else:  # powerball
        # Powerball: 5 numbers from 1-69, Power Ball from 1-26
        main_range = (1, 69)
        mega_range = (1, 26)
        main_count = 5
    
    main_numbers = set()
    while len(main_numbers) < main_count:
        main_numbers.add(random.randint(*main_range))
    
    mega_ball = random.randint(*mega_range)
    
    return {
        'main_numbers': sorted(list(main_numbers)),
        'mega_ball': mega_ball
    }

def generate_seeded_combination(seed_number, game_type='mega_millions'):
    """Generate a lottery combination starting with a specific seed number"""
    if game_type == 'mega_millions':
        main_range = (1, 70)
        mega_range = (1, 25)
        main_count = 5
    else:  # powerball
        main_range = (1, 69)
        mega_range = (1, 26)
        main_count = 5
    
    # Validate seed number is in valid range
    if seed_number < main_range[0] or seed_number > main_range[1]:
        raise ValueError(f"Seed number must be between {main_range[0]} and {main_range[1]} for {game_type}")
    
    # Start with the seed number
    main_numbers = {seed_number}
    
    # Generate remaining numbers
    while len(main_numbers) < main_count:
        main_numbers.add(random.randint(*main_range))
    
    mega_ball = random.randint(*mega_range)
    
    return {
        'main_numbers': sorted(list(main_numbers)),
        'mega_ball': mega_ball
    }

def generate_unique_combinations(count=10, game_type='mega_millions', seed_number=None):
    """Generate unique lottery combinations that haven't been drawn before"""
    drawn_combinations = get_all_drawn_combinations(game_type)
    unique_combinations = []
    attempts = 0
    max_attempts = 1000000  # Safety limit
    
    while len(unique_combinations) < count and attempts < max_attempts:
        if seed_number:
            combination = generate_seeded_combination(seed_number, game_type)
            method = 'seeded'
        else:
            combination = generate_random_combination(game_type)
            method = 'random'
        
        attempts += 1
        
        if not has_been_drawn_before(
            combination['main_numbers'], 
            combination['mega_ball'], 
            drawn_combinations
        ):
            unique_combinations.append(combination)
            
            # Save generated combination
            GeneratedCombination.objects.create(
                main_numbers=', '.join(map(str, combination['main_numbers'])),
                mega_ball=combination['mega_ball'],
                game_type=game_type,
                generation_method=method,
                seed_number=seed_number
            )
    
    return unique_combinations

def check_texas_lottery_numbers(numbers, mega_ball, game_type='mega_millions'):
    """
    Check numbers against Texas Lottery website (simulation)
    Note: This is a simulation since direct API access isn't available
    """
    try:
        # In a real implementation, you would scrape or use an API
        # For now, we'll simulate the check using our database
        recent_draws = LotteryDraw.objects.filter(
            game_type=game_type
        ).order_by('-draw_date')[:10]
        
        matches_found = []
        for draw in recent_draws:
            draw_numbers = draw.get_main_numbers()
            main_matches = len(set(numbers) & set(draw_numbers))
            mega_match = mega_ball == draw.mega_ball
            
            if main_matches >= 2 or mega_match:  # Any significant match
                prize_info = calculate_prize_tier(main_matches, mega_match, game_type)
                matches_found.append({
                    'draw_date': draw.draw_date,
                    'main_matches': main_matches,
                    'mega_match': mega_match,
                    'prize_tier': prize_info['tier'],
                    'estimated_winnings': prize_info['winnings']
                })
        
        return {
            'success': True,
            'matches': matches_found,
            'total_matches': len(matches_found)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'matches': [],
            'total_matches': 0
        }

def calculate_prize_tier(main_matches, mega_match, game_type='mega_millions'):
    """Calculate prize tier based on matches"""
    if game_type == 'mega_millions':
        prize_tiers = {
            (5, True): {'tier': 'Jackpot', 'winnings': 'Jackpot'},
            (5, False): {'tier': 'Match 5', 'winnings': '$1,000,000'},
            (4, True): {'tier': 'Match 4 + MB', 'winnings': '$10,000'},
            (4, False): {'tier': 'Match 4', 'winnings': '$500'},
            (3, True): {'tier': 'Match 3 + MB', 'winnings': '$200'},
            (3, False): {'tier': 'Match 3', 'winnings': '$10'},
            (2, True): {'tier': 'Match 2 + MB', 'winnings': '$10'},
            (1, True): {'tier': 'Match 1 + MB', 'winnings': '$4'},
            (0, True): {'tier': 'Match MB', 'winnings': '$2'},
        }
    else:  # powerball
        prize_tiers = {
            (5, True): {'tier': 'Jackpot', 'winnings': 'Jackpot'},
            (5, False): {'tier': 'Match 5', 'winnings': '$1,000,000'},
            (4, True): {'tier': 'Match 4 + PB', 'winnings': '$50,000'},
            (4, False): {'tier': 'Match 4', 'winnings': '$100'},
            (3, True): {'tier': 'Match 3 + PB', 'winnings': '$100'},
            (3, False): {'tier': 'Match 3', 'winnings': '$7'},
            (2, True): {'tier': 'Match 2 + PB', 'winnings': '$7'},
            (1, True): {'tier': 'Match 1 + PB', 'winnings': '$4'},
            (0, True): {'tier': 'Match PB', 'winnings': '$4'},
        }
    
    return prize_tiers.get((main_matches, mega_match), {'tier': 'No Prize', 'winnings': '$0'})

def check_combination_against_draws(combination, game_type='mega_millions'):
    """Check a saved combination against all historical draws"""
    main_numbers = combination.get_main_numbers_list()
    mega_ball = combination.mega_ball
    
    all_draws = LotteryDraw.objects.filter(game_type=game_type).order_by('-draw_date')
    results = []
    
    for draw in all_draws:
        draw_numbers = draw.get_main_numbers()
        main_matches = len(set(main_numbers) & set(draw_numbers))
        mega_match = mega_ball == draw.mega_ball
        
        if main_matches > 0 or mega_match:
            prize_info = calculate_prize_tier(main_matches, mega_match, game_type)
            
            # Create or update check record
            check_result, created = CombinationCheck.objects.get_or_create(
                saved_combination=combination,
                draw=draw,
                defaults={
                    'matches_main': main_matches,
                    'matches_mega': mega_match,
                    'prize_tier': prize_info['tier'],
                    'estimated_winnings': prize_info['winnings']
                }
            )
            
            results.append(check_result)
    
    return results

def export_combinations_csv(combinations, filename=None):
    """Export combinations to CSV format"""
    if not filename:
        filename = f"lottery_combinations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Date Generated', 'Main Numbers', 'Mega Ball', 'Game Type', 'Method'])
    
    for combo in combinations:
        writer.writerow([
            combo.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
            combo.main_numbers,
            combo.mega_ball,
            combo.get_game_type_display(),
            combo.generation_method
        ])
    
    return response

def export_combinations_excel(combinations, filename=None):
    """Export combinations to Excel format"""
    if not filename:
        filename = f"lottery_combinations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    # Create DataFrame
    data = []
    for combo in combinations:
        data.append({
            'Date Generated': combo.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Main Numbers': combo.main_numbers,
            'Mega Ball': combo.mega_ball,
            'Game Type': combo.get_game_type_display(),
            'Method': combo.generation_method,
            'Seed Number': combo.seed_number if combo.seed_number else 'N/A'
        })
    
    df = pd.DataFrame(data)
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def get_latest_texas_lottery_results(game_type='mega_millions'):
    """
    Fetch latest results from Texas Lottery website (simulation)
    In production, this would scrape the actual website or use an API
    """
    try:
        # Simulate fetching from Texas Lottery website
        # In reality, you would use requests and BeautifulSoup to scrape
        # the Texas Lottery website or use their API if available
        
        # For now, return the latest from our database
        latest_draw = LotteryDraw.objects.filter(
            game_type=game_type
        ).order_by('-draw_date').first()
        
        if latest_draw:
            return {
                'success': True,
                'draw_date': latest_draw.draw_date,
                'winning_numbers': latest_draw.get_main_numbers(),
                'mega_ball': latest_draw.mega_ball,
                'megaplier': latest_draw.megaplier,
                'jackpot': latest_draw.estimated_jackpot
            }
        else:
            return {'success': False, 'error': 'No draws found'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}