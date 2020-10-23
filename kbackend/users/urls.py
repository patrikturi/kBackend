from django.urls import path
from users import views

urlpatterns = [
    path('reset-password/', views.PasswordResetView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('search/', views.UserSearchview.as_view()),
    path('marketplace/', views.PlayerMarketplaceView.as_view()),
    path('profile/<int:user_id>/', views.UserProfileView.as_view()),
    path('test-users/', views.TestUsersView.as_view()),
]
