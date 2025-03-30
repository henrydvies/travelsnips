from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('linked-accounts/', views.linked_accounts_view, name='linked_accounts'),
    path('link-request/<int:user_id>/', views.link_request_view, name='link_request'),
    path('unlink-account/<int:user_id>/', views.unlink_account_view, name='unlink_account'),
]