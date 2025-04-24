from django.db import models

# Create your models here.
from django.db import models

class LotteryDraw(models.Model):
    draw_date = models.DateTimeField()
    winning_numbers = models.CharField(max_length=100)
    mega_ball = models.IntegerField()
    megaplier = models.IntegerField(null=True, blank=True)
    estimated_jackpot = models.CharField(max_length=100, null=True, blank=True)
    jackpot_winners = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Draw on {self.draw_date.strftime('%Y-%m-%d')}: {self.winning_numbers} MB: {self.mega_ball}"
    
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
    
    def __str__(self):
        return f"Generated on {self.generated_date.strftime('%Y-%m-%d')}: {self.main_numbers} MB: {self.mega_ball}"
