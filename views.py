from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import Argon2PasswordHasher
from app_predict.models import *
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404

today = datetime.now().date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

salt = 'w1o2o3d4y5t6o7'
# Create your views here.
def index(request):
    request_time = timezone.now()
    # Lấy tất cả các trận đấu và sắp xếp theo thời gian bắt đầu
    matches = Match.objects.all().order_by('kickoff_time')

    # Lọc các trận đấu theo hôm nay, hôm qua và ngày mai
    matches_today = Match.objects.filter(kickoff_time__date=today).order_by('kickoff_time')
    matches_yesterday = Match.objects.filter(kickoff_time__date=yesterday).order_by('kickoff_time')
    matches_tomorrow = Match.objects.filter(kickoff_time__date=tomorrow).order_by('kickoff_time')

    # Show upcoming matches in right bar
    upcoming_matches = Match.objects.filter(kickoff_time__gt=timezone.now()).order_by('kickoff_time')[:1]
    upcoming_matches1 = Match.objects.filter(kickoff_time__gt=timezone.now()).order_by('kickoff_time')[1:2]
    upcoming_matches2 = Match.objects.filter(kickoff_time__gt=timezone.now()).order_by('kickoff_time')[2:3]

    if 's_user' in request.session:
        user = User.objects.get(pk=request.session.get('s_user')['id'])
        # Tiếp tục xử lý với biến user
        predicted_matches_HDP = PredictionHDP.objects.filter(user=user, match__in=matches,predict_type="HDP")
        predicted_matches_OU = PredictionOU.objects.filter(user=user, match__in=matches,predict_type="OU")
        predicted_matches_1X2 = Prediction1X2.objects.filter(user=user, match__in=matches,predict_type="1X2")

        hdp_count = predicted_matches_HDP.count()
        ou_count = predicted_matches_OU.count()
        HDA_1x2_count = predicted_matches_1X2.count()

        # Tạo một dict lưu thông tin về kết quả dự đoán HDP
        prediction_results_HDP = {}
        for prediction in predicted_matches_HDP:
            match_id = prediction.match.id
            prediction_results_HDP[match_id] = prediction.predicted

        # Tạo một dict lưu thông tin về kết quả dự đoán OU
        prediction_results_OU = {}
        for prediction in predicted_matches_OU:
            match_id = prediction.match.id
            prediction_results_OU[match_id] = prediction.predicted

        # Tạo một dict lưu thông tin về kết quả dự đoán 1X2
        prediction_results_1X2 = {}
        for prediction in predicted_matches_1X2:
            match_id = prediction.match.id
            prediction_results_1X2[match_id] = prediction.predicted

    else:
        user = None
        predicted_matches_HDP = None
        predicted_matches_OU = None
        predicted_matches_1X2 = None
        prediction_results_HDP = None
        prediction_results_OU = None
        prediction_results_1X2 = None
        hdp_count = None
        ou_count = None
        HDA_1x2_count = None

    # Lấy tất cả các dự đoán của trận đấu đang xem xét
    all_hdp_predictions_for_match = PredictionHDP.objects.filter(match__in=matches,predict_type="HDP")
    all_ou_predictions_for_match = PredictionOU.objects.filter(match__in=matches,predict_type="OU")
    all_1x2_predictions_for_match = Prediction1X2.objects.filter(match__in=matches,predict_type="1X2")

    total_hdp_predictions = all_hdp_predictions_for_match.filter(predict_type="HDP").count()
    total_ou_predictions = all_ou_predictions_for_match.filter(predict_type="OU").count()
    total_1x2_predictions = all_1x2_predictions_for_match.filter(predict_type="1X2").count()

    # Đếm số lượng người dùng dự đoán cho home và away
    home_predictions = all_hdp_predictions_for_match.filter(predict_choice='H').values('user').distinct().count()
    away_predictions = all_hdp_predictions_for_match.filter(predict_choice='A').values('user').distinct().count()
    over_predictions = all_ou_predictions_for_match.filter(predict_choice='O').values('user').distinct().count()
    under_predictions = all_ou_predictions_for_match.filter(predict_choice='U').values('user').distinct().count()
    home_1x2_predictions = all_1x2_predictions_for_match.filter(predict_choice='H1').values('user').distinct().count()
    draw_1x2_predictions = all_1x2_predictions_for_match.filter(predict_choice='DX').values('user').distinct().count()
    away_1x2_predictions = all_1x2_predictions_for_match.filter(predict_choice='A2').values('user').distinct().count()

    # Tạo các biến mặc định
    home_percent = 0
    home_decimal = 0
    away_percent = 0
    away_decimal = 0
    over_percent = 0
    over_decimal = 0
    under_percent = 0
    under_decimal = 0
    home_1X2_percent = 0
    home_1X2_decimal = 0
    draw_1x2_percent = 0
    draw_1x2_decimal = 0
    away_1x2_percent = 0
    away_1x2_decimal = 0

    if total_hdp_predictions != 0:

        home_percent = round(home_predictions / total_hdp_predictions * 100)
        home_decimal = home_predictions / total_hdp_predictions if total_hdp_predictions != 0 else 0

        away_percent = round(away_predictions / total_hdp_predictions * 100)
        away_decimal = away_predictions / total_hdp_predictions if total_hdp_predictions != 0 else 0

    if total_ou_predictions != 0:

        over_percent = round(over_predictions / total_ou_predictions * 100)
        over_decimal = over_predictions / total_ou_predictions if total_ou_predictions != 0 else 0

        under_percent = round(under_predictions / total_ou_predictions * 100)
        under_decimal = under_predictions / total_ou_predictions if total_ou_predictions != 0 else 0
    
    if total_1x2_predictions != 0:

        home_1X2_percent = round(home_1x2_predictions / total_1x2_predictions * 100)
        home_1X2_decimal = home_1x2_predictions / total_1x2_predictions if total_1x2_predictions != 0 else 0

        draw_1x2_percent = round(draw_1x2_predictions / total_1x2_predictions * 100)
        draw_1x2_decimal = draw_1x2_predictions / total_1x2_predictions if total_1x2_predictions != 0 else 0

        away_1x2_percent = round(away_1x2_predictions / total_1x2_predictions * 100)
        away_1x2_decimal = away_1x2_predictions / total_1x2_predictions if total_1x2_predictions != 0 else 0


    print(hdp_count)
    print(ou_count)

    return render(request, 'index.html',{
        'matches': matches,
        'matches_today': matches_today,
        'matches_yesterday': matches_yesterday,
        'matches_tomorrow': matches_tomorrow,
        'upcoming_matches': upcoming_matches,
        'upcoming_matches1': upcoming_matches1,
        'upcoming_matches2': upcoming_matches2,
        'predicted_matches_1X2': predicted_matches_1X2,
        'predicted_matches_HDP': predicted_matches_HDP,
        'predicted_matches_OU': predicted_matches_OU,
        'hdp_count': hdp_count,
        'ou_count': ou_count,
        'HDA_1X2_count': HDA_1x2_count,
        'prediction_results_HDP': prediction_results_HDP,
        'prediction_results_OU': prediction_results_OU,
        'prediction_results_1X2': prediction_results_1X2,
        'request_time': request_time,
        'home_percent': home_percent,
        'away_percent': away_percent,
        'over_percent': over_percent,
        'under_percent': under_percent,
        'home_1X2_percent': home_1X2_percent,
        'draw_1x2_percent': draw_1x2_percent,
        'away_1x2_percent': away_1x2_percent,
        'home_decimal': home_decimal,
        'away_decimal': away_decimal,
        'over_decimal': over_decimal,
        'under_decimal': under_decimal,
        'home_1X2_decimal': home_1X2_decimal,
        'draw_1x2_decimal': draw_1x2_decimal,
        'away_1x2_decimal': away_1x2_decimal,
    })














def log_in(request):
    if 's_user' in request.session:
        return redirect('app_predict:index')
    
    #-------------------- [Log in]
    log_in_string = ''
    if request.POST.get('btnLogIn'):
        hasher = Argon2PasswordHasher()
        username = request.POST.get('User').strip()
        password = request.POST.get('Password').strip()
        password_pw = hasher.encode(password,salt)

        user = User.objects.filter(username=username,password=password_pw)
        if user.count() > 0:
            dict_user = user.values()[0]
            request.session['s_user'] = dict_user
            return redirect('app_predict:index')
        else:
            log_in_string = '''
                            <div class="alert alert-danger" role="alert" style="padding: 6px!important;text-align: center;">Incorrect Username or Password.</div>
                            '''

    #-------------------- [Sign Up]
    sign_up_string = ''
    if request.POST.get('btnSignUp'):
        hasher = Argon2PasswordHasher()
        nickname = request.POST.get('Nickname').strip()
        username = request.POST.get('User').strip()
        password = request.POST.get('Password').strip()
        repassword = request.POST.get('Re-enter_PW').strip()

        # Kiểm tra xem nickname hoặc username đã tồn tại hay chưa
        if User.objects.filter(nickname=nickname).exists() or User.objects.filter(username=username).exists():
            sign_up_string = '''
                            <div class="alert alert-danger" role="alert" style="padding: 6px!important;text-align: center;">Failed! This nickname or username already exists!</div>
                            '''
        elif password == repassword:
            User.objects.create(nickname=nickname,
                                username=username,
                                password=hasher.encode(password,salt))
            sign_up_string = '''
                            <div class="alert alert-success" role="alert" style="padding: 6px!important;text-align: center;">Congrats! Your account created Successfully!</div>
                            '''
        else:
            sign_up_string = '''
                            <div class="alert alert-danger" role="alert" style="padding: 6px!important;text-align: center;">Failed! Your account created Was Not Successful!</div>
                            '''



    return render(request, 'login.html',{
        'log_in_string': log_in_string,
        'sign_up_string': sign_up_string,
    })

def log_out (request):

    if 's_user' in request.session:
        del request.session['s_user']

    return redirect('app_predict:log_in')

def change_pw(request):
    result_change_password = ''
    user = request.session.get('s_user')
     # Change Password
    if request.POST.get('btnChangePW'):
        # Gán biến
        hasher = Argon2PasswordHasher() # Tạo biến Hasher mã hóa PW cho User
        current_password = hasher.encode(request.POST.get('current_password'),salt)
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        obj_user = User.objects.get(pk=user['id'])

        # kiểm tra mật khẩu hiện tại (cũ)
        if current_password == obj_user.password:
            if new_password == confirm_password:
                obj_user.password = hasher.encode(new_password, salt)
                obj_user.save()
                result_change_password = '''
                            <div class="alert alert-success" role="alert">
                                Change Password Successfully.
                            </div>
                            '''
            else:
                result_change_password = '''
                            <div class="alert alert-danger" role="alert">
                                New Password and Confirm Password not meet, please try again.
                            </div>
                            '''
        else:
            result_change_password = '''
                            <div class="alert alert-danger" role="alert">
                                Current Password not correct, please try again.
                            </div>
                            '''

    return render(request, 'changepw.html',{
        'result_change_password': result_change_password,
    })

def favorite_matches(request):

    # Lấy danh sách trận đấu yêu thích từ cookie
    favorite_matches = request.COOKIES.get('favorite_matches', '').split(',')
    favorite_match_ids = [int(match_id) for match_id in favorite_matches if match_id.isdigit()]
    favorite_match_details = Match.objects.filter(id__in=favorite_match_ids)

    return render(request, 'favorites.html',{
        'favorite_matches': favorite_matches,
        'favorite_matches2': favorite_match_details,
    })

def toggle_favorite_match(request, match_id):
    
    # Lấy danh sách trận đấu yêu thích từ Cookie (nếu có)
    favorite_matches = request.COOKIES.get('favorite_matches', '').split(',')
    # Xác định xem trận đấu đã được thêm vào yêu thích hay chưa
    if str(match_id) in favorite_matches:   #Nếu trận đấu đã trong danh sách yêu thích, khi click sẽ xóa khỏi yêu thích
        favorite_matches.remove(str(match_id))
        is_favorite = False
    else:
        favorite_matches.append(str(match_id)) #Nếu trận đấu chưa có trong danh sách yêu thích, khi click sẽ thêm vào yêu thích
        is_favorite = True

    # Lưu danh sách yêu thích mới vào Cookie
    response = JsonResponse({'is_favorite': is_favorite})
    response.set_cookie('favorite_matches', ','.join(favorite_matches),max_age=30*24*60*60) # Lưu trữ cookie trong 30 ngày.

    return response

def save_prediction_HDP(request):
 
    if request.method == 'POST':
        # Xử lý lưu dự đoán 
        match_id = request.POST.get('match_id')
        predict_type = request.POST.get('predict_type')
        predict_choice = request.POST.get('predict_choice')
        prediction_value = request.POST.get('prediction')
        predict_odds = request.POST.get('predict_odds')

        user = User.objects.get(pk=request.session.get('s_user')['id'])  # Lấy user hiện tại đang đăng nhập
        match = Match.objects.get(id=match_id)

        # Kiểm tra số lượng dự đoán HDP và OU cho trận đấu
        hdp_predictions_count = PredictionHDP.objects.filter(match=match, predict_type="HDP").count()
        
        if not match.is_prediction_closed:
            if hdp_predictions_count > 0:
                messages.error(request, 'Saved Prediction Failed! This match already has predictions of HDP.')
            else:
                # Nếu chưa có ít nhất một dự đoán loại "HDP" hoặc "OU", cho phép lưu dự đoán:
                prediction = PredictionHDP(user=user, match=match, predict_type=predict_type, predicted=prediction_value,predict_choice=predict_choice,predict_odds=predict_odds)
                prediction.save()
                messages.success(request, 'Prediction saved Successfully!')
        else:
            messages.error(request, 'Saved Prediction Failed! This match prediction already closed before K.O time 1 hour.')
            return redirect('app_predict:index')

    return redirect('app_predict:index')


def save_prediction_OU(request):
 
    if request.method == 'POST':
        # Xử lý lưu dự đoán 
        match_id = request.POST.get('match_id')
        predict_type = request.POST.get('predict_type')
        predict_choice = request.POST.get('predict_choice')
        prediction_value = request.POST.get('prediction')
        predict_odds = request.POST.get('predict_odds')

        user = User.objects.get(pk=request.session.get('s_user')['id'])  # Lấy user hiện tại đang đăng nhập
        match = Match.objects.get(id=match_id)

        # Kiểm tra số lượng dự đoán OU cho trận đấu
        ou_predictions_count = PredictionOU.objects.filter(match=match, predict_type="OU").count()
        
        if not match.is_prediction_closed:
            if ou_predictions_count > 0:
                messages.error(request, 'Saved Prediction Failed! This match already has predictions OU.')
            else:
                # Nếu chưa có ít nhất một dự đoán loại "OU", cho phép lưu dự đoán:
                prediction = PredictionOU(user=user, match=match, predict_type=predict_type, predicted=prediction_value,predict_choice=predict_choice,predict_odds=predict_odds)
                prediction.save()
                messages.success(request, 'Prediction saved Successfully!')
        else:
            messages.error(request, 'Saved Prediction Failed! This match prediction already closed before K.O time 1 hour.')
            return redirect('app_predict:index')

    return redirect('app_predict:index')


def save_prediction_1X2(request):
 
    if request.method == 'POST':
        # Xử lý lưu dự đoán 
        match_id = request.POST.get('match_id')
        predict_type = request.POST.get('predict_type')
        predict_choice = request.POST.get('predict_choice')
        prediction_value = request.POST.get('prediction')
        predict_odds = request.POST.get('predict_odds')

        user = User.objects.get(pk=request.session.get('s_user')['id'])  # Lấy user hiện tại đang đăng nhập
        match = Match.objects.get(id=match_id)

        # Kiểm tra số lượng dự đoán HDP và OU cho trận đấu
        HDA1X2_predictions_count = Prediction1X2.objects.filter(match=match, predict_type="1X2").count()
        
        if not match.is_prediction_closed:
            if HDA1X2_predictions_count > 0:
                messages.error(request, 'Saved Prediction Failed! This match already has predictions of both types (HDP and OU).')
            else:
                # Nếu chưa có ít nhất một dự đoán loại "HDP" hoặc "OU", cho phép lưu dự đoán:
                prediction = Prediction1X2(user=user, match=match, predict_type=predict_type, predicted=prediction_value,predict_choice=predict_choice,predict_odds=predict_odds)
                prediction.save()
                messages.success(request, 'Prediction saved Successfully!')
        else:
            messages.error(request, 'Saved Prediction Failed! This match prediction already closed before K.O time 1 hour.')
            return redirect('app_predict:index')

    return redirect('app_predict:index')

def delete_prediction_HDP(request, prediction_id):
    if 's_user' in request.session and request.method == 'POST':
        # Xác định và xóa dự đoán dựa trên prediction_id
        user = User.objects.get(pk=request.session.get('s_user')['id'])
        prediction = get_object_or_404(PredictionHDP, pk=prediction_id,user=user)
        
        # Lấy match_id của dự đoán đang xóa
        match_id = prediction.match.pk
        
        # Xóa dự đoán cụ thể chỉ nếu nó thuộc về người dùng hiện tại
        prediction.delete()
        
        messages.success(request, 'Prediction has been deleted successfully!')

    return redirect('app_predict:index')

def delete_prediction_OU(request, prediction_id):
    if 's_user' in request.session and request.method == 'POST':
        # Xác định và xóa dự đoán dựa trên prediction_id
        user = User.objects.get(pk=request.session.get('s_user')['id'])
        prediction = get_object_or_404(PredictionOU, pk=prediction_id,user=user)
        
        # Lấy match_id của dự đoán đang xóa
        match_id = prediction.match.pk
        
        # Xóa dự đoán cụ thể chỉ nếu nó thuộc về người dùng hiện tại
        prediction.delete()
        
        messages.success(request, 'Prediction has been deleted successfully!')

    return redirect('app_predict:index')

def delete_prediction_1X2(request, prediction_id):
    if 's_user' in request.session and request.method == 'POST':
        # Xác định và xóa dự đoán dựa trên prediction_id
        user = User.objects.get(pk=request.session.get('s_user')['id'])
        prediction = get_object_or_404(Prediction1X2, pk=prediction_id,user=user)
        
        # Lấy match_id của dự đoán đang xóa
        match_id = prediction.match.pk
        
        # Xóa dự đoán cụ thể chỉ nếu nó thuộc về người dùng hiện tại
        prediction.delete()
        
        messages.success(request, 'Prediction has been deleted successfully!')

    return redirect('app_predict:index')

# Hàm xử lý điều kiện hiển thị trạng thái trận đấu
def match_status(request_time, kickoff_time):
    if request_time < kickoff_time:
        return kickoff_time.strftime('%d %b %H:%M')  # Hiển thị giờ kickoff_time

    elif request_time == kickoff_time and kickoff_time < kickoff_time + timezone.timedelta(hours=2):
        return 'LIVE'  # Hiển thị LIVE nếu đúng trạng thái

    elif request_time > kickoff_time + timezone.timedelta(hours=2):
        return 'Finished'  # Hiển thị Finished nếu đúng trạng thái

    # Nếu không phù hợp với bất kỳ trạng thái nào trên
    return None