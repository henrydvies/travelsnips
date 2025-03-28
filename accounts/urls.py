from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Example future path for user profile
    # path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
]