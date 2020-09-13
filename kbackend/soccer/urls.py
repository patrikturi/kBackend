from django.urls import path
from soccer import views

urlpatterns = [
    path('stats/', views.SoccerStats.as_view()),
]
