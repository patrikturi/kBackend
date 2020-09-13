from django.urls import path
from soccer import views

urlpatterns = [
    path('stats/', views.SoccerStats.as_view()),
    path('matches/', views.Matches.as_view()),
]
