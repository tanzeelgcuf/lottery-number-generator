from django.contrib import admin
from .models import (
    LotteryDraw, GeneratedCombination, SavedCombination, 
    CombinationCheck, ExportLog, NumberFrequency, UserProfile,
    SmartPrediction, NumberPattern, WinningAlert, NumberStatistics,
    SyndicatePool, SyndicateMembership, PoolCombination
)

@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = ['game_type', 'draw_date', 'winning_numbers', 'mega_ball', 'estimated_jackpot']
    list_filter = ['game_type', 'draw_date']
    search_fields = ['winning_numbers']

@admin.register(GeneratedCombination)
class GeneratedCombinationAdmin(admin.ModelAdmin):
    list_display = ['generated_date', 'game_type', 'generation_method', 'main_numbers', 'mega_ball', 'user']
    list_filter = ['game_type', 'generation_method', 'generated_date']

@admin.register(SavedCombination)
class SavedCombinationAdmin(admin.ModelAdmin):
    list_display = ['combination_name', 'user', 'game_type', 'main_numbers', 'mega_ball', 'created_date', 'is_active']
    list_filter = ['game_type', 'created_date', 'is_active', 'is_favorite']
    search_fields = ['combination_name', 'user__username']

@admin.register(NumberFrequency)
class NumberFrequencyAdmin(admin.ModelAdmin):
    list_display = ['game_type', 'number', 'is_mega_ball', 'frequency', 'last_drawn']
    list_filter = ['game_type', 'is_mega_ball']
    ordering = ['-frequency']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_game', 'total_combinations_generated', 'total_combinations_saved', 'member_since']
    list_filter = ['preferred_game', 'member_since']

@admin.register(SmartPrediction)
class SmartPredictionAdmin(admin.ModelAdmin):
    list_display = ['game_type', 'prediction_date', 'algorithm_used', 'confidence_score', 'is_active']
    list_filter = ['game_type', 'algorithm_used', 'is_active']

@admin.register(WinningAlert)
class WinningAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'combination', 'prize_tier', 'estimated_winnings', 'alert_date', 'is_read']
    list_filter = ['prize_tier', 'is_read', 'alert_date']

@admin.register(SyndicatePool)
class SyndicatePoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'game_type', 'max_members', 'created_date', 'is_active']
    list_filter = ['game_type', 'is_active', 'created_date']

admin.site.register(CombinationCheck)
admin.site.register(ExportLog)
admin.site.register(NumberPattern)
admin.site.register(NumberStatistics)
admin.site.register(SyndicateMembership)
admin.site.register(PoolCombination)