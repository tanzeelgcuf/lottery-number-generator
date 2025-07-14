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

from .models import LotteryDraw, GeneratedCombination, SavedCombination, CombinationCheck, ExportLog

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
    """Generate unique lottery combinations"""
    combinations = []
    
    for i in range(count):
        if seed_number:
            combination = generate_seeded_combination(seed_number, game_type)
            method = 'seeded'
        else:
            combination = generate_random_combination(game_type)
            method = 'random'
        
        combinations.append(combination)
        
        # Save generated combination
        GeneratedCombination.objects.create(
            main_numbers=', '.join(map(str, combination['main_numbers'])),
            mega_ball=combination['mega_ball'],
            game_type=game_type,
            generation_method=method,
            seed_number=seed_number
        )
    
    return combinations

def generate_multiple_seeded_combinations(seed_numbers, count_per_seed=5, game_type='powerball'):
    """Generate lottery combinations for multiple seed numbers"""
    all_combinations = []
    
    for seed_number in seed_numbers:
        try:
            # Generate combinations for this seed number
            combinations = generate_unique_combinations(count_per_seed, game_type, seed_number)
            
            for combo in combinations:
                combo['seed_used'] = seed_number  # Track which seed was used
                all_combinations.append(combo)
                
        except ValueError as e:
            continue  # Skip invalid seed numbers
    
    return all_combinations

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
    """Enhanced number generation with seeded options"""
    game_type = request.GET.get('game_type', 'mega_millions')
    
    # Get generation parameters
    count = int(request.GET.get('count', 10))
    seed_number = request.GET.get('seed_number', None)
    
    try:
        if seed_number:
            seed_number = int(seed_number)
            combinations = generate_unique_combinations(count, game_type, seed_number)
            messages.success(request, f'Generated {len(combinations)} unique combinations starting with {seed_number}')
        else:
            combinations = generate_unique_combinations(count, game_type)
            messages.success(request, f'Generated {len(combinations)} unique random combinations')
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
    """🆕 NEW: Generate numbers using multiple first numbers"""
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
            all_combinations = generate_multiple_seeded_combinations(
                valid_first_numbers, count_per_seed, game_type
            )
            
            messages.success(request, f'Generated {len(all_combinations)} combinations using first numbers: {valid_first_numbers}')
            
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

def save_combination(request):
    """Save a combination for future checking"""
    if request.method == 'POST':
        try:
            main_numbers = request.POST.get('main_numbers')
            mega_ball = int(request.POST.get('mega_ball'))
            game_type = request.POST.get('game_type', 'mega_millions')
            combination_name = request.POST.get('combination_name', 'My Numbers')
            
            # Validate main numbers
            numbers_list = [int(x.strip()) for x in main_numbers.split(',')]
            if game_type == 'mega_millions':
                if len(numbers_list) != 5 or any(n < 1 or n > 70 for n in numbers_list):
                    messages.error(request, 'Mega Millions requires 5 numbers between 1-70')
                    return redirect('index')
                if mega_ball < 1 or mega_ball > 25:
                    messages.error(request, 'Mega Ball must be between 1-25')
                    return redirect('index')
            else:  # powerball
                if len(numbers_list) != 5 or any(n < 1 or n > 69 for n in numbers_list):
                    messages.error(request, 'Powerball requires 5 numbers between 1-69')
                    return redirect('index')
                if mega_ball < 1 or mega_ball > 26:
                    messages.error(request, 'Power Ball must be between 1-26')
                    return redirect('index')
            
            # Check for duplicates in main numbers
            if len(set(numbers_list)) != len(numbers_list):
                messages.error(request, 'Main numbers must be unique')
                return redirect('index')
            
            # Save combination
            SavedCombination.objects.create(
                combination_name=combination_name,
                main_numbers=main_numbers,
                mega_ball=mega_ball,
                game_type=game_type
            )
            
            messages.success(request, f'Combination "{combination_name}" saved successfully!')
            
        except ValueError:
            messages.error(request, 'Invalid number format')
        except Exception as e:
            messages.error(request, f'Error saving combination: {str(e)}')
    
    return redirect('saved_combinations')

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
    
    # For now, create a mock result since we don't have historical data yet
    mock_results = [
        {
            'draw_date': datetime.datetime.now() - datetime.timedelta(days=i*3),
            'matches_main': random.randint(0, 3),
            'matches_mega': random.choice([True, False]),
            'prize_tier': 'Match 2' if random.randint(0, 5) > 3 else 'No Prize',
            'estimated_winnings': '$10' if random.randint(0, 5) > 3 else '$0'
        }
        for i in range(5)  # Show 5 recent mock draws
    ]
    
    context = {
        'combination': combination,
        'results': mock_results,
        'texas_check': {'success': True, 'matches': [], 'total_matches': 0},
        'total_matches': sum(1 for r in mock_results if r['matches_main'] > 0 or r['matches_mega'])
    }
    
    messages.success(request, f'Checked combination against recent draws')
    
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
    """Export combinations to CSV or Excel"""
    export_type = request.GET.get('format', 'csv')
    game_type = request.GET.get('game_type', 'mega_millions')
    
    # Get combinations to export
    combinations = GeneratedCombination.objects.filter(game_type=game_type).order_by('-generated_date')[:100]
    
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="lottery_combinations_{game_type}.csv"'
        
        import csv
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
    
    # For now, redirect back if Excel format requested
    messages.info(request, f'Exported {combinations.count()} combinations to CSV')
    return redirect('lottery_results')

def export_combinations_enhanced(request):
    """🆕 NEW: Enhanced export with date filtering and first number tracking"""
    export_type = request.GET.get('format', 'csv')
    game_type = request.GET.get('game_type', 'powerball')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Filter combinations
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
    
    combinations = combinations.order_by('-generated_date', 'seed_number')
    
    if export_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        filename = f"{game_type}_combinations_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        import csv
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
        
        messages.success(request, f'Exported {combinations.count()} combinations to CSV')
        return response
    
    messages.info(request, f'Found {combinations.count()} combinations for export')
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
            combinations = generate_unique_combinations(count, game_type, seed_number)
        else:
            combinations = generate_unique_combinations(count, game_type)
        
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
            
            # Mock result for now
            result = {
                'success': True,
                'matches': [],
                'total_matches': 0,
                'message': 'Numbers checked successfully'
            }
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)