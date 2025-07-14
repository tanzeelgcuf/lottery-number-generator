from django.db import models
from django.contrib.auth.models import User

class LotteryDraw(models.Model):
    GAME_CHOICES = [
        ('mega_millions', 'Mega Millions'),
        ('powerball', 'Powerball'),
    ]
    
    game_type = models.CharField(max_length=20, choices=GAME_CHOICES, default='mega_millions')
    draw_date = models.DateTimeField()
    winning_numbers = models.CharField(max_length=100)
    mega_ball = models.IntegerField()  # This will be power_ball for Powerball games
    megaplier = models.IntegerField(null=True, blank=True)  # This will be power_play for Powerball
    estimated_jackpot = models.CharField(max_length=100, null=True, blank=True)
    jackpot_winners = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_game_type_display()} - {self.draw_date.strftime('%Y-%m-%d')}: {self.winning_numbers} MB: {self.mega_ball}"
    
    def get_main_numbers(self):
        """Parse the winning numbers string into a list of integers"""
        return [int(num.strip()) for num in self.winning_numbers.split('-')]
    
    def get_combination_key(self):
        """Get a unique key representing this combination"""
        main_numbers = sorted(self.get_main_numbers())
        return f"{'-'.join(map(str, main_numbers))}-MB-{self.mega_ball}"

class GeneratedCombination(models.Model):
    """Model to store generated combinations for reference"""
    generated_date = models.DateTimeField(auto_now_add=True)
    main_numbers = models.CharField(max_length=100)
    mega_ball = models.IntegerField()
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES, default='mega_millions')
    generation_method = models.CharField(max_length=50, default='random')  # 'random', 'seeded', 'manual'
    seed_number = models.IntegerField(null=True, blank=True)  # First number used as seed
    
    def __str__(self):
        return f"Generated on {self.generated_date.strftime('%Y-%m-%d')}: {self.main_numbers} MB: {self.mega_ball}"

class SavedCombination(models.Model):
    """Model to store user-saved combinations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    combination_name = models.CharField(max_length=100, default="My Numbers")
    main_numbers = models.CharField(max_length=100)
    mega_ball = models.IntegerField()
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES, default='mega_millions')
    created_date = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.combination_name}: {self.main_numbers} MB: {self.mega_ball}"
    
    def get_main_numbers_list(self):
        """Parse the main numbers string into a list of integers"""
        return [int(num.strip()) for num in self.main_numbers.split(',')]

class CombinationCheck(models.Model):
    """Model to store results of checking combinations against draws"""
    saved_combination = models.ForeignKey(SavedCombination, on_delete=models.CASCADE)
    draw = models.ForeignKey(LotteryDraw, on_delete=models.CASCADE)
    matches_main = models.IntegerField(default=0)  # Number of main numbers matched
    matches_mega = models.BooleanField(default=False)  # Whether mega ball matched
    check_date = models.DateTimeField(auto_now_add=True)
    prize_tier = models.CharField(max_length=50, null=True, blank=True)
    estimated_winnings = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        unique_together = ['saved_combination', 'draw']
    
    def __str__(self):
        return f"Check: {self.saved_combination.combination_name} vs {self.draw.draw_date.strftime('%Y-%m-%d')}"

class ExportLog(models.Model):
    """Model to track exported combination lists"""
    export_date = models.DateTimeField(auto_now_add=True)
    export_type = models.CharField(max_length=20, choices=[('csv', 'CSV'), ('excel', 'Excel')])
    file_name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    combinations_count = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Export {self.export_type} on {self.export_date.strftime('%Y-%m-%d')}: {self.combinations_count} combinations"