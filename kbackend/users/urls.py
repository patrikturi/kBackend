from django.urls import path
from users import views

urlpatterns = [
    path('reset-password/', views.PasswordReset.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('search/', views.UserSearch.as_view()),
    path('marketplace/', views.PlayerMarketplace.as_view()),
]
