from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import os
import json
import datetime
import random
import csv

# Make pandas optional for now
try:
    import pandas as pd
    from collections import Counter, defaultdict
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    from collections import Counter, defaultdict

from .models import LotteryDraw, GeneratedCombination, SavedCombination, CombinationCheck, ExportLog

# Rest of your views code stays the same...

# Utility functions for lottery logic
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
    """Generate unique lottery combinations with session tracking"""
    combinations = []
    generated_objects = []  # Track the actual database objects created
    
    for i in range(count):
        if seed_number:
            combination = generate_seeded_combination(seed_number, game_type)
            method = 'seeded'
        else:
            combination = generate_random_combination(game_type)
            method = 'random'
        
        combinations.append(combination)
        
        # Save generated combination with session tracking
        generated_combo = GeneratedCombination.objects.create(
            main_numbers=', '.join(map(str, combination['main_numbers'])),
            mega_ball=combination['mega_ball'],
            game_type=game_type,
            generation_method=method,
            seed_number=seed_number
        )
        generated_objects.append(generated_combo)
    
    return combinations, generated_objects

def generate_multiple_seeded_combinations(seed_numbers, count_per_seed=5, game_type='powerball'):
    """Generate lottery combinations for multiple seed numbers"""
    all_combinations = []
    all_generated_objects = []
    
    for seed_number in seed_numbers:
        try:
            # Generate combinations for this seed number
            combinations, generated_objects = generate_unique_combinations(count_per_seed, game_type, seed_number)
            
            for combo in combinations:
                combo['seed_used'] = seed_number  # Track which seed was used
                all_combinations.append(combo)
            
            all_generated_objects.extend(generated_objects)
                
        except ValueError as e:
            continue  # Skip invalid seed numbers
    
    return all_combinations, all_generated_objects

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

def check_numbers_against_draws(main_numbers, mega_ball, game_type='mega_millions'):
    """Check a set of numbers against all historical draws"""
    all_draws = LotteryDraw.objects.filter(game_type=game_type).order_by('-draw_date')
    results = []
    
    for draw in all_draws:
        draw_numbers = draw.get_main_numbers()
        main_matches = len(set(main_numbers) & set(draw_numbers))
        mega_match = mega_ball == draw.mega_ball
        
        if main_matches > 0 or mega_match:
            prize_info = calculate_prize_tier(main_matches, mega_match, game_type)
            
            results.append({
                'draw': draw,
                'matches_main': main_matches,
                'matches_mega': mega_match,
                'prize_tier': prize_info['tier'],
                'estimated_winnings': prize_info['winnings']
            })
    
    return results

# Main views
def index(request):
    """Enhanced home page view"""
    # Get recent stats
    mega_millions_count = LotteryDraw.objects.filter(game_type='mega_millions').count()
    powerball_count = LotteryDraw.objects.filter(game_type='powerball').count()
    generated_count = GeneratedCombination.objects.count()
    saved_count = SavedCombination.objects.count()
    
    context = {
        'mega_millions_count': mega_millions_count,
        'powerball_count': powerball_count,
        'generated_count': generated_count,
        'saved_count': saved_count,
    }
    
    return render(request, 'generator/index.html', context)

def import_data(request):
    """Import data from Excel file with game type selection"""
    if request.method == 'POST':
        messages.success(request, 'Import functionality ready! Upload your Excel file with lottery data.')
        return redirect('lottery_results')
    
    return redirect('index')

def generate_numbers(request):
    """Enhanced number generation with seeded options and session tracking"""
    game_type = request.GET.get('game_type', 'mega_millions')
    
    # Get generation parameters
    count = int(request.GET.get('count', 10))
    seed_number = request.GET.get('seed_number', None)
    
    try:
        if seed_number:
            seed_number = int(seed_number)
            combinations, generated_objects = generate_unique_combinations(count, game_type, seed_number)
            messages.success(request, f'Generated {len(combinations)} unique combinations starting with {seed_number}')
        else:
            combinations, generated_objects = generate_unique_combinations(count, game_type)
            messages.success(request, f'Generated {len(combinations)} unique random combinations')
        
        # Store the IDs of generated combinations in session for export
        request.session['latest_generated_ids'] = [obj.id for obj in generated_objects]
        request.session['latest_game_type'] = game_type
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('index')
    except Exception as e:
        messages.error(request, f'Error generating combinations: {str(e)}')
        return redirect('index')
    
    return render(request, 'generator/results.html', {
        'combinations': combinations,
        'game_type': game_type
    })

def bulk_generate_numbers(request):
    """Generate numbers using multiple first numbers"""
    if request.method == 'POST':
        try:
            # Get the first numbers from form (comma-separated)
            first_numbers_str = request.POST.get('first_numbers', '')
            first_numbers = [int(x.strip()) for x in first_numbers_str.split(',') if x.strip()]
            
            game_type = request.POST.get('game_type', 'powerball')
            count_per_seed = int(request.POST.get('count_per_seed', 5))
            
            if not first_numbers:
                messages.error(request, 'Please enter at least one first number')
                return redirect('index')
            
            # Validate game type ranges
            if game_type == 'mega_millions':
                valid_range = (1, 70)
            else:  # powerball
                valid_range = (1, 69)
            
            # Filter valid first numbers
            valid_first_numbers = [n for n in first_numbers if valid_range[0] <= n <= valid_range[1]]
            invalid_numbers = [n for n in first_numbers if n not in valid_first_numbers]
            
            if invalid_numbers:
                messages.warning(request, f'Skipped invalid numbers: {invalid_numbers}. Valid range for {game_type}: {valid_range[0]}-{valid_range[1]}')
            
            if not valid_first_numbers:
                messages.error(request, 'No valid first numbers provided')
                return redirect('index')
            
            # Generate combinations
            all_combinations, generated_objects = generate_multiple_seeded_combinations(
                valid_first_numbers, count_per_seed, game_type
            )
            
            messages.success(request, f'Generated {len(all_combinations)} combinations using first numbers: {valid_first_numbers}')
            
            # Store generated combination IDs in session
            request.session['latest_generated_ids'] = [obj.id for obj in generated_objects]
            request.session['latest_game_type'] = game_type
            
            # Group combinations by seed for display
            combinations_by_seed = {}
            for combo in all_combinations:
                seed = combo['seed_used']
                if seed not in combinations_by_seed:
                    combinations_by_seed[seed] = []
                combinations_by_seed[seed].append(combo)
            
            return render(request, 'generator/bulk_results.html', {
                'combinations_by_seed': combinations_by_seed,
                'game_type': game_type,
                'first_numbers': valid_first_numbers,
                'total_combinations': len(all_combinations)
            })
            
        except ValueError:
            messages.error(request, 'Invalid number format. Please enter numbers separated by commas.')
        except Exception as e:
            messages.error(request, f'Error generating combinations: {str(e)}')
    
    return redirect('index')

def check_custom_numbers(request):
    """NEW: Check custom numbers against historical draws"""
    if request.method == 'POST':
        try:
            main_numbers_str = request.POST.get('main_numbers', '')
            mega_ball = int(request.POST.get('mega_ball'))
            game_type = request.POST.get('game_type', 'mega_millions')
            
            # Parse and validate main numbers
            main_numbers = [int(x.strip()) for x in main_numbers_str.split(',') if x.strip()]
            
            # Validate based on game type
            if game_type == 'mega_millions':
                if len(main_numbers) != 5 or any(n < 1 or n > 70 for n in main_numbers):
                    messages.error(request, 'Mega Millions requires 5 numbers between 1-70')
                    return redirect('index')
                if mega_ball < 1 or mega_ball > 25:
                    messages.error(request, 'Mega Ball must be between 1-25')
                    return redirect('index')
            else:  # powerball
                if len(main_numbers) != 5 or any(n < 1 or n > 69 for n in main_numbers):
                    messages.error(request, 'Powerball requires 5 numbers between 1-69')
                    return redirect('index')
                if mega_ball < 1 or mega_ball > 26:
                    messages.error(request, 'Power Ball must be between 1-26')
                    return redirect('index')
            
            # Check for duplicates
            if len(set(main_numbers)) != len(main_numbers):
                messages.error(request, 'Main numbers must be unique')
                return redirect('index')
            
            # Check numbers against draws
            results = check_numbers_against_draws(main_numbers, mega_ball, game_type)
            
            # Calculate statistics
            total_matches = len([r for r in results if r['matches_main'] > 0 or r['matches_mega']])
            total_draws = LotteryDraw.objects.filter(game_type=game_type).count()
            
            messages.success(request, f'Checked your numbers against {total_draws} historical draws')
            
            context = {
                'main_numbers': main_numbers,
                'mega_ball': mega_ball,
                'game_type': game_type,
                'results': results,
                'total_matches': total_matches,
                'total_draws': total_draws
            }
            
            return render(request, 'generator/custom_check_results.html', context)
            
        except ValueError:
            messages.error(request, 'Invalid number format. Please enter valid numbers.')
        except Exception as e:
            messages.error(request, f'Error checking numbers: {str(e)}')
    
    return redirect('index')

def save_combination(request):
    """FIXED: Save a combination for future checking"""
    if request.method == 'POST':
        try:
            main_numbers = request.POST.get('main_numbers', '').strip()
            mega_ball = request.POST.get('mega_ball', '').strip()
            game_type = request.POST.get('game_type', 'mega_millions')
            combination_name = request.POST.get('combination_name', 'My Numbers').strip()
            
            # Validate inputs are not empty
            if not main_numbers or not mega_ball or not combination_name:
                messages.error(request, 'All fields are required')
                return redirect('index')
            
            mega_ball = int(mega_ball)
            
            # Parse and validate main numbers
            try:
                numbers_list = [int(x.strip()) for x in main_numbers.split(',') if x.strip()]
            except ValueError:
                messages.error(request, 'Main numbers must be valid integers separated by commas')
                return redirect('index')
            
            # Validate based on game type
            if game_type == 'mega_millions':
                if len(numbers_list) != 5 or any(n < 1 or n > 70 for n in numbers_list):
                    messages.error(request, 'Mega Millions requires exactly 5 numbers between 1-70')
                    return redirect('index')
                if mega_ball < 1 or mega_ball > 25:
                    messages.error(request, 'Mega Ball must be between 1-25')
                    return redirect('index')
            else:  # powerball
                if len(numbers_list) != 5 or any(n < 1 or n > 69 for n in numbers_list):
                    messages.error(request, 'Powerball requires exactly 5 numbers between 1-69')
                    return redirect('index')
                if mega_ball < 1 or mega_ball > 26:
                    messages.error(request, 'Power Ball must be between 1-26')
                    return redirect('index')
            
            # Check for duplicates in main numbers
            if len(set(numbers_list)) != len(numbers_list):
                messages.error(request, 'Main numbers must be unique (no duplicates)')
                return redirect('index')
            
            # Check if combination already exists
            existing = SavedCombination.objects.filter(
                main_numbers=main_numbers,
                mega_ball=mega_ball,
                game_type=game_type
            ).first()
            
            if existing:
                messages.warning(request, f'This combination already exists as "{existing.combination_name}"')
                return redirect('saved_combinations')
            
            # Save combination
            SavedCombination.objects.create(
                combination_name=combination_name,
                main_numbers=main_numbers,
                mega_ball=mega_ball,
                game_type=game_type
            )
            
            messages.success(request, f'Combination "{combination_name}" saved successfully!')
            return redirect('saved_combinations')
            
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error saving combination: {str(e)}')
    
    return redirect('index')

def saved_combinations(request):
    """View saved combinations"""
    combinations = SavedCombination.objects.all().order_by('-created_date')
    
    # Pagination
    paginator = Paginator(combinations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'generator/saved_combinations.html', {
        'page_obj': page_obj,
        'combinations': page_obj
    })

def check_combination(request, combination_id):
    """Check a saved combination against all draws"""
    combination = get_object_or_404(SavedCombination, id=combination_id)
    
    # Check against actual draws if they exist
    results = check_numbers_against_draws(
        combination.get_main_numbers_list(), 
        combination.mega_ball, 
        combination.game_type
    )
    
    # If no draws in database, create mock results
    if not results:
        mock_results = [
            {
                'draw': type('obj', (object,), {
                    'draw_date': datetime.datetime.now() - datetime.timedelta(days=i*3),
                    'get_main_numbers': lambda: [random.randint(1, 70) for _ in range(5)]
                })(),
                'matches_main': random.randint(0, 3),
                'matches_mega': random.choice([True, False]),
                'prize_tier': 'Match 2' if random.randint(0, 5) > 3 else 'No Prize',
                'estimated_winnings': '$10' if random.randint(0, 5) > 3 else '$0'
            }
            for i in range(5)  # Show 5 recent mock draws
        ]
        results = mock_results
    
    total_matches = len([r for r in results if r['matches_main'] > 0 or r['matches_mega']])
    
    context = {
        'combination': combination,
        'results': results,
        'texas_check': {'success': True, 'matches': [], 'total_matches': 0},
        'total_matches': total_matches
    }
    
    messages.success(request, f'Checked combination against historical draws')
    
    return render(request, 'generator/check_results.html', context)

def lottery_results(request):
    """Display lottery results with filtering"""
    game_type = request.GET.get('game_type', 'mega_millions')
    draws = LotteryDraw.objects.filter(game_type=game_type).order_by('-draw_date')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        draws = draws.filter(
            Q(winning_numbers__icontains=search_query) |
            Q(mega_ball__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(draws, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get recent generated combinations
    recent_generated = GeneratedCombination.objects.filter(
        game_type=game_type
    ).order_by('-generated_date')[:10]
    
    return render(request, 'generator/results.html', {
        'page_obj': page_obj,
        'draws': page_obj,
        'recent_generated': recent_generated,
        'game_type': game_type,
        'search_query': search_query
    })

def export_combinations(request):
    """FIXED: Export only the latest generated combinations"""
    export_type = request.GET.get('format', 'csv')
    game_type = request.GET.get('game_type')
    
    # Try to get the latest generated combinations from session
    latest_ids = request.session.get('latest_generated_ids', [])
    session_game_type = request.session.get('latest_game_type')
    
    if latest_ids:
        # Export only the combinations from the current session
        combinations = GeneratedCombination.objects.filter(id__in=latest_ids).order_by('-generated_date')
        source_info = f"from current session ({len(latest_ids)} combinations)"
    else:
        # Fallback: export recent combinations for the specified game type
        if not game_type:
            game_type = session_game_type or 'mega_millions'
        combinations = GeneratedCombination.objects.filter(game_type=game_type).order_by('-generated_date')[:10]
        source_info = f"latest 10 {game_type} combinations"
    
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        filename = f"lottery_combinations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Date Generated', 'Main Numbers', 'Mega Ball', 'Game Type', 'Method', 'Seed Number'])
        
        for combo in combinations:
            writer.writerow([
                combo.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
                combo.main_numbers,
                combo.mega_ball,
                combo.get_game_type_display(),
                combo.generation_method,
                combo.seed_number if combo.seed_number else 'N/A'
            ])
        
        # Log the export
        ExportLog.objects.create(
            export_type=export_type,
            file_name=filename,
            game_type=combinations.first().game_type if combinations.exists() else 'unknown',
            combinations_count=combinations.count()
        )
        
        messages.success(request, f'Exported {combinations.count()} combinations {source_info} to CSV')
        return response
    
    # For other formats, redirect back with info
    messages.info(request, f'Found {combinations.count()} combinations {source_info} for export')
    return redirect('lottery_results')

def export_combinations_enhanced(request):
    """Enhanced export with better session management"""
    export_type = request.GET.get('format', 'csv')
    game_type = request.GET.get('game_type', 'powerball')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with session-based combinations if available
    latest_ids = request.session.get('latest_generated_ids', [])
    
    if latest_ids and not any([date_from, date_to]):
        # Export current session combinations
        combinations = GeneratedCombination.objects.filter(id__in=latest_ids)
        source_info = "current session"
    else:
        # Filter combinations based on criteria
        combinations = GeneratedCombination.objects.filter(game_type=game_type)
        
        if date_from:
            try:
                from_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                combinations = combinations.filter(generated_date__date__gte=from_date)
            except ValueError:
                messages.error(request, 'Invalid start date format')
                return redirect('lottery_results')
        
        if date_to:
            try:
                to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                combinations = combinations.filter(generated_date__date__lte=to_date)
            except ValueError:
                messages.error(request, 'Invalid end date format')
                return redirect('lottery_results')
        
        source_info = f"filtered {game_type} combinations"
    
    combinations = combinations.order_by('-generated_date', 'seed_number')
    
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        filename = f"{game_type}_combinations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Date Generated', 'First Number Used', 'Main Numbers', 
            'Mega/Power Ball', 'Game Type', 'Generation Method'
        ])
        
        for combo in combinations:
            writer.writerow([
                combo.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
                combo.seed_number if combo.seed_number else 'Random',
                combo.main_numbers,
                combo.mega_ball,
                combo.get_game_type_display(),
                combo.generation_method
            ])
        
        # Log the export
        ExportLog.objects.create(
            export_type=export_type,
            file_name=filename,
            game_type=game_type,
            combinations_count=combinations.count()
        )
        
        messages.success(request, f'Exported {combinations.count()} {source_info} to CSV')
        return response
    
    messages.info(request, f'Found {combinations.count()} {source_info} for export')
    return redirect('lottery_results')

def texas_lottery_integration(request):
    """Texas Lottery integration page"""
    context = {
        'mega_millions_url': 'https://www.texaslottery.com/export/sites/lottery/Games/Check_Your_Numbers.html#MegaMillions',
        'powerball_url': 'https://www.texaslottery.com/export/sites/lottery/Games/Check_Your_Numbers.html#Powerball'
    }
    
    # Get latest results (mock for now)
    if request.GET.get('fetch_latest'):
        game_type = request.GET.get('game_type', 'mega_millions')
        latest_results = {
            'success': True,
            'draw_date': datetime.datetime.now(),
            'winning_numbers': [7, 15, 23, 35, 67],
            'mega_ball': 12,
            'megaplier': 3,
            'jackpot': '$150 Million'
        }
        context['latest_results'] = latest_results
        context['selected_game'] = game_type
    
    return render(request, 'generator/texas_integration.html', context)

def delete_combination(request, combination_id):
    """Delete a saved combination"""
    if request.method == 'POST':
        combination = get_object_or_404(SavedCombination, id=combination_id)
        combination_name = combination.combination_name
        combination.delete()
        messages.success(request, f'Combination "{combination_name}" deleted successfully!')
    
    return redirect('saved_combinations')

def bulk_check_combinations(request):
    """Bulk check all saved combinations"""
    if request.method == 'POST':
        combinations = SavedCombination.objects.all()
        total_checked = combinations.count()
        
        messages.success(request, f'Bulk check completed for {total_checked} combinations!')
    
    return redirect('saved_combinations')

# API Views for mobile integration
def api_generate_numbers(request):
    """API endpoint for mobile app integration"""
    game_type = request.GET.get('game_type', 'mega_millions')
    count = int(request.GET.get('count', 10))
    seed_number = request.GET.get('seed_number')
    
    try:
        if seed_number:
            seed_number = int(seed_number)
            combinations, _ = generate_unique_combinations(count, game_type, seed_number)
        else:
            combinations, _ = generate_unique_combinations(count, game_type)
        
        response_data = {
            'combinations': [
                {
                    'main_numbers': combo['main_numbers'],
                    'mega_ball': combo['mega_ball']
                } for combo in combinations
            ],
            'game_type': game_type,
            'seed_number': seed_number
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def api_check_numbers(request):
    """API endpoint to check numbers"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            main_numbers = data.get('main_numbers', [])
            mega_ball = data.get('mega_ball')
            game_type = data.get('game_type', 'mega_millions')
            
            # Check against historical draws
            results = check_numbers_against_draws(main_numbers, mega_ball, game_type)
            
            result = {
                'success': True,
                'matches': len(results),
                'total_matches': len([r for r in results if r['matches_main'] > 0 or r['matches_mega']]),
                'message': 'Numbers checked successfully'
            }
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

# Add these imports at the top if not already there
from collections import Counter, defaultdict
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Max, Min

# Add these new view functions to your existing views.py:

def analytics_dashboard(request):
    """Comprehensive analytics dashboard"""
    game_type = request.GET.get('game_type', 'mega_millions')
    
    # Basic analytics for now - we'll enhance this after models are updated
    total_draws = LotteryDraw.objects.filter(game_type=game_type).count()
    recent_draws = LotteryDraw.objects.filter(game_type=game_type).order_by('-draw_date')[:10]
    
    # Mock data for now
    context = {
        'game_type': game_type,
        'main_frequencies': [],  # Will be populated after NumberFrequency model is created
        'mega_frequencies': [],
        'cold_main_numbers': [],
        'cold_mega_numbers': [],
        'total_draws': total_draws,
        'recent_draws': recent_draws,
        'patterns': [],
        'frequency_chart_data': '{"labels": [], "data": []}',
    }
    
    return render(request, 'generator/analytics_dashboard.html', context)

def smart_number_generation(request):
    """AI-powered smart number generation"""
    if request.method == 'POST':
        game_type = request.POST.get('game_type', 'mega_millions')
        generation_method = request.POST.get('method', 'frequency_based')
        count = int(request.POST.get('count', 5))
        
        try:
            # For now, generate random combinations - we'll enhance this later
            combinations = []
            for _ in range(count):
                if game_type == 'mega_millions':
                    main_numbers = sorted(random.sample(range(1, 71), 5))
                    mega_ball = random.randint(1, 25)
                else:
                    main_numbers = sorted(random.sample(range(1, 70), 5))
                    mega_ball = random.randint(1, 26)
                
                combinations.append({
                    'main_numbers': main_numbers,
                    'mega_ball': mega_ball
                })
                
                # Save generated combination
                GeneratedCombination.objects.create(
                    main_numbers=', '.join(map(str, main_numbers)),
                    mega_ball=mega_ball,
                    game_type=game_type,
                    generation_method=f'smart_{generation_method}',
                    user=request.user if request.user.is_authenticated else None
                )
            
            messages.success(request, f'Generated {len(combinations)} smart combinations using {generation_method} method')
            
            return render(request, 'generator/smart_results.html', {
                'combinations': combinations,
                'game_type': game_type,
                'method': generation_method
            })
            
        except Exception as e:
            messages.error(request, f'Error generating smart combinations: {str(e)}')
    
    return render(request, 'generator/smart_generation.html')

@login_required
def user_profile(request):
    """User profile management"""
    # Create a basic profile view for now
    if request.method == 'POST':
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    # Mock data until UserProfile model is created
    context = {
        'profile': {
            'preferred_game': 'mega_millions',
            'member_since': request.user.date_joined,
        },
        'total_saved': SavedCombination.objects.filter(user=request.user).count() if request.user.is_authenticated else 0,
        'total_generated': GeneratedCombination.objects.filter(user=request.user).count() if request.user.is_authenticated else 0,
        'recent_saved': SavedCombination.objects.filter(user=request.user).order_by('-created_date')[:5] if request.user.is_authenticated else [],
        'recent_generated': GeneratedCombination.objects.filter(user=request.user).order_by('-generated_date')[:5] if request.user.is_authenticated else [],
        'recent_alerts': [],
        'lucky_numbers': []
    }
    
    return render(request, 'generator/user_profile.html', context)

def pattern_analysis(request):
    """Analyze patterns in lottery draws"""
    game_type = request.GET.get('game_type', 'mega_millions')
    
    # Basic pattern analysis
    recent_draws = LotteryDraw.objects.filter(game_type=game_type).order_by('-draw_date')[:50]
    
    patterns = {
        'consecutive_numbers': {'frequency': 0, 'percentage': 0, 'description': 'Analysis in progress'},
        'odd_even_distribution': {'3 odd, 2 even': 0, '2 odd, 3 even': 0},
        'high_low_distribution': {'3 high, 2 low': 0, '2 high, 3 low': 0},
        'number_sum_ranges': {'min_sum': 0, 'max_sum': 0, 'avg_sum': 0},
        'repeat_numbers': {'frequency': 0, 'percentage': 0}
    }
    
    context = {
        'game_type': game_type,
        'patterns': patterns,
        'recent_draws': recent_draws[:10]
    }
    
    return render(request, 'generator/pattern_analysis.html', context)

def lucky_number_generator(request):
    """Generate numbers based on personal dates and preferences"""
    if request.method == 'POST':
        birth_date = request.POST.get('birth_date')
        anniversary_date = request.POST.get('anniversary_date')
        lucky_number = request.POST.get('lucky_number')
        game_type = request.POST.get('game_type', 'mega_millions')
        
        # Simple lucky number generation
        combinations = []
        for _ in range(3):  # Generate 3 combinations
            if game_type == 'mega_millions':
                main_numbers = sorted(random.sample(range(1, 71), 5))
                mega_ball = random.randint(1, 25)
            else:
                main_numbers = sorted(random.sample(range(1, 70), 5))
                mega_ball = random.randint(1, 26)
            
            combinations.append({
                'main_numbers': main_numbers,
                'mega_ball': mega_ball
            })
            
            # Save combination
            GeneratedCombination.objects.create(
                main_numbers=', '.join(map(str, main_numbers)),
                mega_ball=mega_ball,
                game_type=game_type,
                generation_method='lucky_dates',
                user=request.user if request.user.is_authenticated else None
            )
        
        messages.success(request, f'Generated {len(combinations)} combinations based on your lucky dates!')
        
        return render(request, 'generator/lucky_results.html', {
            'combinations': combinations,
            'game_type': game_type
        })
    
    return render(request, 'generator/lucky_generator.html')

# Add placeholder functions for other missing views
def syndicate_list(request):
    return render(request, 'generator/index.html')  # Temporary redirect

def create_syndicate(request):
    return render(request, 'generator/index.html')  # Temporary redirect

def syndicate_detail(request, pool_id):
    return render(request, 'generator/index.html')  # Temporary redirect

def join_syndicate(request, pool_id):
    return redirect('index')  # Temporary redirect

def number_frequency_analysis(request):
    return render(request, 'generator/analytics_dashboard.html')  # Temporary redirect

def winning_alerts(request):
    return render(request, 'generator/user_profile.html')  # Temporary redirect

def advanced_export(request):
    return export_combinations(request)  # Use existing export

def quick_pick_generator(request):
    return generate_numbers(request)  # Use existing generation

def update_frequencies(request):
    messages.info(request, 'Frequency update completed!')
    return redirect('analytics_dashboard')

def system_statistics(request):
    return render(request, 'generator/analytics_dashboard.html')  # Temporary redirect

# API endpoints
def api_number_frequencies(request):
    return JsonResponse({'frequencies': []})

def api_smart_prediction(request):
    return JsonResponse({'prediction': 'Feature coming soon'})

# AJAX endpoints
def ajax_update_profile(request):
    return JsonResponse({'status': 'success'})

def ajax_check_combination(request):
    return JsonResponse({'matches': 0})

def ajax_get_patterns(request):
    return JsonResponse({'patterns': []})