from django.urls import path
from soccer import views

urlpatterns = [
    path('stats/', views.SoccerStatsView.as_view()),
    path('matches/', views.MatchesView.as_view()),
]
