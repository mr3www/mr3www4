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


@receiver(post_save, sender=PredictionHDP, weak=False)
def update_buy_counts_hdp(sender, instance, created, **kwargs):
    if not signal_locked:  # Kiểm tra signal có bị tắt không
        lock_signal()  # Tắt signal trước khi cập nhật
        match = instance.match

        if instance.predict_choice in ('H', 'A'):
            buy_home_count = PredictionHDP.objects.filter(match=match, predict_choice='H').count()
            buy_away_count = PredictionHDP.objects.filter(match=match, predict_choice='A').count()
            match.buy_home = buy_home_count
            match.buy_away = buy_away_count

        match.save()  # Lưu thông tin sau khi đã cập nhật
        unlock_signal()  # Bật lại signal sau khi hoàn tất cập nhật

@receiver(post_delete, sender=PredictionHDP)
def delete_buy_counts_hdp(sender, instance, **kwargs):
    if not signal_locked:  # Kiểm tra signal có bị tắt không
        lock_signal()  # Tắt signal trước khi cập nhật
        match = instance.match

        if instance.predict_choice in ('H', 'A'):
            buy_home_count = PredictionHDP.objects.filter(match=match, predict_choice='H').count()
            buy_away_count = PredictionHDP.objects.filter(match=match, predict_choice='A').count()
            match.buy_home = buy_home_count
            match.buy_away = buy_away_count

        match.save()  # Lưu thông tin sau khi đã cập nhật
        unlock_signal()  # Bật lại signal sau khi hoàn tất cập nhật

#------------------------------------------ Count OVER/UNDER
@receiver(post_save, sender=PredictionOU, weak=False)
def update_buy_counts_ou(sender, instance, created, **kwargs):
    if not signal_locked:  # Kiểm tra signal có bị tắt không
        lock_signal()  # Tắt signal trước khi cập nhật
        match = instance.match

        if instance.predict_choice in ('O', 'U'):
            buy_over_count = PredictionOU.objects.filter(match=match, predict_choice='O').count()
            buy_under_count = PredictionOU.objects.filter(match=match, predict_choice='U').count()
            match.buy_over = buy_over_count
            match.buy_under = buy_under_count

        match.save()  # Lưu thông tin sau khi đã cập nhật
        unlock_signal()  # Bật lại signal sau khi hoàn tất cập nhật

@receiver(post_delete, sender=PredictionOU)
def delete_buy_counts_ou(sender, instance, **kwargs):
    if not signal_locked:  # Kiểm tra signal có bị tắt không
        lock_signal()  # Tắt signal trước khi cập nhật
        match = instance.match

        if instance.predict_choice in ('O', 'U'):
            buy_over_count = PredictionOU.objects.filter(match=match, predict_choice='O').count()
            buy_under_count = PredictionOU.objects.filter(match=match, predict_choice='U').count()
            match.buy_over = buy_over_count
            match.buy_under = buy_under_count

        match.save()  # Lưu thông tin sau khi đã cập nhật
        unlock_signal()  # Bật lại signal sau khi hoàn tất cập nhật

