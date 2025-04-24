from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LotteryDraw, GeneratedCombination

@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = ('draw_date', 'winning_numbers', 'mega_ball', 'megaplier', 'estimated_jackpot')
    list_filter = ('draw_date',)
    search_fields = ('winning_numbers',)
    date_hierarchy = 'draw_date'

@admin.register(GeneratedCombination)
class GeneratedCombinationAdmin(admin.ModelAdmin):
    list_display = ('generated_date', 'main_numbers', 'mega_ball')
    list_filter = ('generated_date',)
    date_hierarchy = 'generated_date'
