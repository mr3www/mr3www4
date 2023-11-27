from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from app_predict.models import *
from import_export import resources
# from django.utils.html import format_html

# Register your models here.
class MatchResource(resources.ModelResource):
    class Meta:
        model = Match

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password','nickname','profit','profit_claim',)

class MatchAdmin(ImportExportModelAdmin):
    resource_class = MatchResource
    list_display = ('id','kickoff_time', 'league', 'home_team', 'away_team','home_score',
                    'away_score','handicap_H','home_odds','away_odds','ou_U','over_odds',
                    'under_odds','buy_home','buy_away','buy_over','buy_under','buy_h1','buy_dx','buy_a2','created_day', )

class PredictionHDPAdmin(admin.ModelAdmin):
    list_display = ('id','user','match','predict_type','predict_choice','predicted','predict_odds','profit','created_day',)

class PredictionOUAdmin(admin.ModelAdmin):
    list_display = ('id','user','match','predict_type','predict_choice','predicted','predict_odds','profit','created_day',)

class Prediction1X2Admin(admin.ModelAdmin):
    list_display = ('id','user','match','predict_type','predict_choice','predicted','predict_odds','profit','created_day',)

class RewardAdmin(admin.ModelAdmin):
    list_display = ('reward_type', 'quantity_available', 'name', 'image','price','status','user_redeemed','note','created_day', )



admin.site.register(User, UserAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(PredictionHDP, PredictionHDPAdmin)
admin.site.register(PredictionOU, PredictionOUAdmin)
admin.site.register(Prediction1X2, Prediction1X2Admin)
admin.site.register(Reward, RewardAdmin)


admin.site.site_header ='Scorebox.Games Administration'