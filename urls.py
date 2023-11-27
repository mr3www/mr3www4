from django.urls import path
from app_predict.views import *
from . import views


app_name = 'app_predict'
urlpatterns = [
  path('', index, name='index'),
  path('login/', log_in, name='log_in'),
  path('logout/', log_out, name='log_out'),
  path('change-password/', change_pw, name='change_pw'),
  path('favorite-matches/', favorite_matches, name='favorite_matches'),
  path('toggle_favorite_match/<int:match_id>/', views.toggle_favorite_match, name='toggle_favorite_match'),
  path('save_prediction_HDP/', views.save_prediction_HDP, name='save_prediction_HDP'),
  path('save_prediction_OU/', views.save_prediction_OU, name='save_prediction_OU'),
  path('save_prediction_1X2/', views.save_prediction_1X2, name='save_prediction_1X2'),
  path('delete_prediction_HDP/<int:prediction_id>/', views.delete_prediction_HDP, name='delete_prediction_HDP'),
  path('delete_prediction_OU/<int:prediction_id>/', views.delete_prediction_OU, name='delete_prediction_OU'),
  path('delete_prediction_1X2/<int:prediction_id>/', views.delete_prediction_1X2, name='delete_prediction_1X2'),

#   path('league/<int:league_id>/', league_matches, name='league_matches'),
#   path('profile/', profile, name='profile'),

]
