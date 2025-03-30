from django.urls import path
from . import views

urlpatterns = [
    path('create_post/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
]