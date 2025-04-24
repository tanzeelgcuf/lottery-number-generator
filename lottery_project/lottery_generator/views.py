from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os
import pandas as pd
from django.http import JsonResponse

from .models import LotteryDraw, GeneratedCombination
from .utils import parse_excel_data, generate_unique_combinations

def index(request):
    """Home page view"""
    return render(request, 'lottery_generator/index.html')

def import_data(request):
    """Import data from Excel file"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']
        
        # Create media directory if it doesn't exist
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir, exist_ok=True)
        
        # Save the file temporarily
        temp_file_path = os.path.join(media_dir, 'temp_lottery_data.xlsx')
        with open(temp_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Parse the data and import to database
        parse_excel_data(temp_file_path)
        
        # Clean up
        os.remove(temp_file_path)
        
        return redirect('lottery_results')
    
    return redirect('index')

def generate_numbers(request):
    """Generate unique lottery numbers"""
    # Check if we have data in the database
    if LotteryDraw.objects.count() == 0:
        return render(request, 'lottery_generator/index.html', {
            'error': 'Please import lottery data first'
        })
    
    # Generate unique combinations
    count = int(request.GET.get('count', 10))  # Default to 10 sets
    combinations = generate_unique_combinations(count)
    
    return render(request, 'lottery_generator/results.html', {
        'combinations': combinations
    })

def lottery_results(request):
    """Display all lottery results"""
    draws = LotteryDraw.objects.all().order_by('-draw_date')[:50]  # Show the last 50 draws
    return render(request, 'lottery_generator/results.html', {
        'draws': draws
    })

def api_generate_numbers(request):
    '''API endpoint for mobile app integration'''
    # Check if we have data in the database
    if LotteryDraw.objects.count() == 0:
        return JsonResponse({
            'error': 'No lottery data available'
        }, status=400)
    
    # Generate unique combinations
    count = int(request.GET.get('count', 10))  # Default to 10 sets
    combinations = generate_unique_combinations(count)
    
    # Format response
    response_data = {
        'combinations': [
            {
                'main_numbers': combo['main_numbers'],
                'mega_ball': combo['mega_ball']
            } for combo in combinations
        ]
    }
    
    return JsonResponse(response_data)