from django.urls import path
from users import views

urlpatterns = [
    path('reset-password/', views.PasswordReset.as_view()),
]
