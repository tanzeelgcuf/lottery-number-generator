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
    path('bulk-generate/', views.bulk_generate_numbers, name='bulk_generate_numbers'),
    
    # Custom number checking
    path('check-custom/', views.check_custom_numbers, name='check_custom_numbers'),
    
    # Saved combinations management
    path('save-combination/', views.save_combination, name='save_combination'),
    path('saved-combinations/', views.saved_combinations, name='saved_combinations'),
    path('check-combination/<int:combination_id>/', views.check_combination, name='check_combination'),
    path('delete-combination/<int:combination_id>/', views.delete_combination, name='delete_combination'),
    path('bulk-check/', views.bulk_check_combinations, name='bulk_check_combinations'),
    
    # Export functionality
    path('export/', views.export_combinations, name='export_combinations'),
    path('export-enhanced/', views.export_combinations_enhanced, name='export_combinations_enhanced'),
    
    # Texas Lottery integration
    path('texas-lottery/', views.texas_lottery_integration, name='texas_lottery_integration'),
    
    # NEW: Enhanced Features
    
    # Analytics and Statistics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('pattern-analysis/', views.pattern_analysis, name='pattern_analysis'),
    
    # Smart Generation
    path('smart-generation/', views.smart_number_generation, name='smart_number_generation'),
    path('lucky-generator/', views.lucky_number_generator, name='lucky_number_generator'),
    
    # User Management
    path('profile/', views.user_profile, name='user_profile'),
    
    # Syndicate/Pool Management
    path('create-syndicate/', views.create_syndicate, name='create_syndicate'),
    path('syndicate/<int:pool_id>/', views.syndicate_detail, name='syndicate_detail'),
    path('syndicates/', views.syndicate_list, name='syndicate_list'),
    path('join-syndicate/<int:pool_id>/', views.join_syndicate, name='join_syndicate'),
    
    # Advanced Features
    path('number-frequency/', views.number_frequency_analysis, name='number_frequency_analysis'),
    path('winning-alerts/', views.winning_alerts, name='winning_alerts'),
    path('export-advanced/', views.advanced_export, name='advanced_export'),
    path('quick-pick/', views.quick_pick_generator, name='quick_pick_generator'),
    
    # Data Management
    path('update-frequencies/', views.update_frequencies, name='update_frequencies'),
    path('system-stats/', views.system_statistics, name='system_statistics'),
    
    # API endpoints for mobile integration
    path('api/generate/', views.api_generate_numbers, name='api_generate_numbers'),
    path('api/check/', views.api_check_numbers, name='api_check_numbers'),
    path('api/frequencies/', views.api_number_frequencies, name='api_number_frequencies'),
    path('api/smart-predict/', views.api_smart_prediction, name='api_smart_prediction'),
    
    # AJAX endpoints for dynamic features
    path('ajax/update-profile/', views.ajax_update_profile, name='ajax_update_profile'),
    path('ajax/check-combination/', views.ajax_check_combination, name='ajax_check_combination'),
    path('ajax/get-patterns/', views.ajax_get_patterns, name='ajax_get_patterns'),
]