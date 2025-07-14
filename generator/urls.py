from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('results/', views.lottery_results, name='lottery_results'),
    
    # Data import
    path('import/', views.import_data, name='import_data'),
    
    # Number generation
    path('generate/', views.generate_numbers, name='generate_numbers'),
    path('bulk-generate/', views.bulk_generate_numbers, name='bulk_generate_numbers'),  # 🆕 NEW
    
    # Saved combinations management
    path('save-combination/', views.save_combination, name='save_combination'),
    path('saved-combinations/', views.saved_combinations, name='saved_combinations'),
    path('check-combination/<int:combination_id>/', views.check_combination, name='check_combination'),
    path('delete-combination/<int:combination_id>/', views.delete_combination, name='delete_combination'),
    path('bulk-check/', views.bulk_check_combinations, name='bulk_check_combinations'),
    
    # Export functionality
    path('export/', views.export_combinations, name='export_combinations'),
    path('export-enhanced/', views.export_combinations_enhanced, name='export_combinations_enhanced'),  # 🆕 NEW
    
    # Texas Lottery integration
    path('texas-lottery/', views.texas_lottery_integration, name='texas_lottery_integration'),
    
    # API endpoints for mobile integration
    path('api/generate/', views.api_generate_numbers, name='api_generate_numbers'),
    path('api/check/', views.api_check_numbers, name='api_check_numbers'),
]