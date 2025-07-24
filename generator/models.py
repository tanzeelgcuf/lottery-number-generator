from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json

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
    generation_method = models.CharField(max_length=50, default='random')  # 'random', 'seeded', 'manual', 'smart'
    seed_number = models.IntegerField(null=True, blank=True)  # First number used as seed
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
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
    is_active = models.BooleanField(default=True)  # For tracking if still playing these numbers
    notes = models.TextField(blank=True, null=True)  # Personal notes about the combination
    
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
    export_type = models.CharField(max_length=20, choices=[('csv', 'CSV'), ('excel', 'Excel'), ('pdf', 'PDF')])
    file_name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    combinations_count = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Export {self.export_type} on {self.export_date.strftime('%Y-%m-%d')}: {self.combinations_count} combinations"

# NEW MODELS FOR ENHANCED FEATURES

class NumberFrequency(models.Model):
    """Track frequency of numbers in historical draws"""
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    number = models.IntegerField()
    is_mega_ball = models.BooleanField(default=False)
    frequency = models.IntegerField(default=0)
    last_drawn = models.DateTimeField(null=True, blank=True)
    days_since_drawn = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['game_type', 'number', 'is_mega_ball']
    
    def __str__(self):
        ball_type = "Mega Ball" if self.is_mega_ball else "Main"
        return f"{self.game_type} - {ball_type} {self.number}: {self.frequency} times"

class UserProfile(models.Model):
    """Extended user profile for lottery preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_game = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES, default='mega_millions')
    lucky_numbers = models.CharField(max_length=200, blank=True, null=True)  # JSON array of lucky numbers
    notification_preferences = models.JSONField(default=dict)  # Email, SMS preferences
    total_combinations_generated = models.IntegerField(default=0)
    total_combinations_saved = models.IntegerField(default=0)
    member_since = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_lucky_numbers(self):
        """Parse lucky numbers from JSON"""
        if self.lucky_numbers:
            try:
                return json.loads(self.lucky_numbers)
            except:
                return []
        return []

class SmartPrediction(models.Model):
    """AI-powered number predictions based on patterns"""
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    prediction_date = models.DateTimeField(auto_now_add=True)
    predicted_numbers = models.CharField(max_length=100)  # Main numbers
    predicted_mega_ball = models.IntegerField()
    confidence_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    algorithm_used = models.CharField(max_length=50, default='frequency_analysis')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Prediction for {self.game_type} on {self.prediction_date.strftime('%Y-%m-%d')}"

class NumberPattern(models.Model):
    """Track patterns in lottery draws"""
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    pattern_type = models.CharField(max_length=50)  # 'consecutive', 'odd_even', 'high_low', etc.
    pattern_description = models.CharField(max_length=200)
    frequency = models.IntegerField(default=0)
    last_occurrence = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.game_type} - {self.pattern_type}: {self.frequency} occurrences"

class WinningAlert(models.Model):
    """Store winning notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    combination = models.ForeignKey(SavedCombination, on_delete=models.CASCADE)
    draw = models.ForeignKey(LotteryDraw, on_delete=models.CASCADE)
    prize_tier = models.CharField(max_length=50)
    estimated_winnings = models.CharField(max_length=100)
    alert_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Alert for {self.user.username}: {self.prize_tier}"

class NumberStatistics(models.Model):
    """Overall statistics for number analysis"""
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    stat_type = models.CharField(max_length=50)  # 'hottest_number', 'coldest_number', 'most_common_pair', etc.
    stat_value = models.CharField(max_length=200)
    calculation_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.game_type} - {self.stat_type}: {self.stat_value}"

class SyndicatePool(models.Model):
    """Group play functionality"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pools')
    members = models.ManyToManyField(User, through='SyndicateMembership')
    game_type = models.CharField(max_length=20, choices=LotteryDraw.GAME_CHOICES)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    max_members = models.IntegerField(default=10)
    
    def __str__(self):
        return f"Pool: {self.name} ({self.members.count()} members)"

class SyndicateMembership(models.Model):
    """Membership in lottery pools"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pool = models.ForeignKey(SyndicatePool, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    contribution_share = models.FloatField(default=1.0)  # Equal shares by default
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'pool']

class PoolCombination(models.Model):
    """Combinations played by syndicate pools"""
    pool = models.ForeignKey(SyndicatePool, on_delete=models.CASCADE)
    main_numbers = models.CharField(max_length=100)
    mega_ball = models.IntegerField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.pool.name}: {self.main_numbers} MB: {self.mega_ball}"