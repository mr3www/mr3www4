from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=150, unique=True)
    profit = models.FloatField(default=0.0)  # Thay đổi DecimalField thành FloatField
    profit_claim = models.FloatField(default=0.0)

    def __str__(self):
        return self.nickname


class Match(models.Model):
    kickoff_time = models.DateTimeField()
    league = models.CharField(max_length=200)
    home_team = models.CharField(max_length=200)
    away_team = models.CharField(max_length=200)
    handicap_H = models.FloatField(null=True, blank=True)
    handicap_A = models.FloatField(null=True, blank=True)
    home_odds = models.FloatField(null=True, blank=True)
    away_odds = models.FloatField(null=True, blank=True)
    ou_O = models.FloatField(null=True, blank=True)
    ou_U = models.FloatField(null=True, blank=True)
    over_odds = models.FloatField(null=True, blank=True)
    under_odds = models.FloatField(null=True, blank=True)
    HDA_1 = models.FloatField(null=True, blank=True)
    HDA_X = models.FloatField(null=True, blank=True)
    HDA_2 = models.FloatField(null=True, blank=True)
    prediction_closing_time = models.DurationField(default=timezone.timedelta(minutes=60))
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    buy_home = models.IntegerField(default=0)
    buy_away = models.IntegerField(default=0)
    buy_over = models.IntegerField(default=0)
    buy_under = models.IntegerField(default=0)
    buy_h1 = models.IntegerField(default=0)
    buy_dx = models.IntegerField(default=0)
    buy_a2 = models.IntegerField(default=0)
    created_day = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.home_team} vs. {self.away_team} - {self.kickoff_time}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Kiểm tra xem đối tượng đã tồn tại trong database chưa, nếu chưa thì là đang tạo mới
            # Đặt mặc định cho prediction_closing_time trước 1 tiếng nếu đang tạo mới đối tượng
            self.prediction_closing_time = timezone.timedelta(minutes=60)
        super().save(*args, **kwargs)
    
    @property
    def is_prediction_closed(self):
        return timezone.now() >= self.kickoff_time - self.prediction_closing_time
    
    def display_status(self):
        current_time = timezone.now()

        if current_time < self.kickoff_time:
            return self.kickoff_time.strftime("%d %b %H:%M")  # Giờ bắt đầu nếu chưa diễn ra
        elif current_time <= self.kickoff_time + timezone.timedelta(hours=2):
            return "LIVE"  # Nếu đang diễn ra
        else:
            return "Finished"  # Nếu đã kết thúc
    
    def calculate_results(self):
        results = {}
        fields = ['home_odds', 'away_odds', 'over_odds', 'under_odds','HDA_1','HDA_X','HDA_2',]
        for field in fields:
            odds = getattr(self, field)
            if odds is not None:
                win = (odds - 1) * 20
                win_half = (odds - 1) * 20 / 2
                lose = -20
                lose_half = -10
                results[field + '_results'] = {
                    'win': win,
                    'win_half': win_half,
                    'lose': lose,
                    'lose_half': lose_half
                }
            else:
                results[field + '_results'] = {
                    'win': None,
                    'win_half': None,
                    'lose': None,
                    'lose_half': None
                }
        return results
    
    def buy_home_percentage(self):
        total_predictions = self.buy_home + self.buy_away
        if total_predictions > 0:
            percentage = (self.buy_home / total_predictions) * 100
        else:
            percentage = 0
        return round(percentage, 2)

    def buy_away_percentage(self):
        total_predictions = self.buy_home + self.buy_away
        if total_predictions > 0:
            percentage = (self.buy_away / total_predictions) * 100
        else:
            percentage = 0
        return round(percentage, 2)
    
    def buy_over_percentage(self):
        total_predictions = self.buy_over + self.buy_under
        if total_predictions > 0:
            percentage = (self.buy_over / total_predictions) * 100
        else:
            percentage = 0
        return round(percentage, 2)
    
    def buy_under_percentage(self):
        total_predictions = self.buy_over + self.buy_under
        if total_predictions > 0:
            percentage = (self.buy_under / total_predictions) * 100
        else:
            percentage = 0
        return round(percentage, 2)
    
    def buy_home_decimal(self):
        total_predictions = self.buy_home + self.buy_away
        if total_predictions > 0:
            decimal = self.buy_home / total_predictions
        else:
            decimal = 0
        return round(decimal, 2)

    def buy_away_decimal(self):
        total_predictions = self.buy_home + self.buy_away
        if total_predictions > 0:
            decimal = self.buy_away / total_predictions
        else:
            decimal = 0
        return round(decimal, 2)
    
    def buy_over_decimal(self):
        total_predictions = self.buy_over + self.buy_under
        if total_predictions > 0:
            decimal = self.buy_over / total_predictions
        else:
            decimal = 0
        return round(decimal, 2)
    
    def buy_under_decimal(self):
        total_predictions = self.buy_over + self.buy_under
        if total_predictions > 0:
            decimal = (self.buy_under / total_predictions) 
        else:
            decimal = 0
        return round(decimal, 2)

class PredictionHDP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    
    predict_choice = models.CharField(max_length=200) #H,A
    predict_type = models.CharField(max_length=200, null=True, blank= True) #HDP
    predict_odds = models.FloatField(null=True, blank=True) #1.95,...
    predicted = models.FloatField(null=True, blank=True) #-0.5, 0.5,...

    profit = models.DecimalField(max_digits=100, decimal_places=2, default=0.0)
    created_day = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.match.home_team} vs. {self.match.away_team} - {self.predict_choice}"
    
class PredictionOU(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    
    predict_choice = models.CharField(max_length=200) #O,U
    predict_type = models.CharField(max_length=200, null=True, blank= True) #OU
    predict_odds = models.FloatField(null=True, blank=True) #1.95,...
    predicted = models.FloatField(null=True, blank=True) #-2.5, 2.75,...

    profit = models.DecimalField(max_digits=100, decimal_places=2, default=0.0)
    created_day = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.match.home_team} vs. {self.match.away_team} - {self.predict_choice}"
    
class Prediction1X2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    
    predict_choice = models.CharField(max_length=200) #H1,DX,A2
    predict_type = models.CharField(max_length=200, null=True, blank= True) # 1X2
    predict_odds = models.FloatField(null=True, blank=True) #1.95,...
    predicted = models.FloatField(null=True, blank=True) #-0.5, 2.5,...

    profit = models.DecimalField(max_digits=100, decimal_places=2, default=0.0)
    created_day = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.match.home_team} vs. {self.match.away_team} - {self.predict_choice}"

class Reward(models.Model):
    reward_type = models.CharField(max_length=50)  # Ví dụ: 'Normal', 'Special'
    quantity_available = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='reward_images/')
    price = models.DecimalField(max_digits=100, decimal_places=2)
    status = models.BooleanField(default=False)  # Đã được đổi hay chưa
    user_redeemed = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_day = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
