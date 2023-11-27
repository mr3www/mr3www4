from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *

# Tạo biến để lưu trạng thái signal
signal_locked = False

# Function để tạm thời tắt signal
def lock_signal():
    global signal_locked
    signal_locked = True

# Function để bật lại signal
def unlock_signal():
    global signal_locked
    signal_locked = False


def update_prediction_profit(prediction, home_score, away_score):
    if prediction.predict_choice == 'H':
        result = home_score - away_score + float(prediction.predicted)
    elif prediction.predict_choice == 'A':
        result = away_score - home_score + float(prediction.predicted)
    elif prediction.predict_choice == 'O':
        result = (home_score + away_score) + float(prediction.predicted)
    elif prediction.predict_choice == 'U':
        result = float(prediction.predicted) - (home_score + away_score)

    if result >= 0.5:
        profit = 20 * (float(prediction.predict_odds) - 1)
    elif result >= 0.25:
        profit = (20 * (float(prediction.predict_odds) - 1)) / 2
    elif result > -0.25: 
        profit = 0
    elif result > -0.5:
        profit = -10
    else:
        profit = -20

    prediction.profit = profit
    prediction.save()

    prediction.user.profit += profit
    prediction.user.profit_claim += profit
    prediction.user.save()

@receiver(post_save, sender=Match, weak=False)
def update_scores_and_profits(sender, instance, created, **kwargs):
    if not created and not signal_locked:  # Kiểm tra signal có bị tắt không
        lock_signal()  # Tắt signal trước khi cập nhật
        home_score = instance.home_score
        away_score = instance.away_score
        
        # Cập nhật thông tin trong Match
        instance.save()  # Lưu thông tin sau khi đã cập nhật
        
        # Bật lại signal sau khi hoàn tất cập nhật
        unlock_signal()

        # Xử lý cho PredictionHDP
        predictions_hdp = PredictionHDP.objects.filter(match=instance)
        for prediction_hdp in predictions_hdp:
            update_prediction_profit(prediction_hdp, home_score, away_score)

        # Xử lý cho PredictionOU
        predictions_ou = PredictionOU.objects.filter(match=instance)
        for prediction_ou in predictions_ou:
            update_prediction_profit(prediction_ou, home_score, away_score)

        # Xử lý cho Prediction1X2
        predictions_1x2 = Prediction1X2.objects.filter(match=instance)
        for prediction_1x2 in predictions_1x2:
            update_prediction_profit(prediction_1x2, home_score, away_score)


