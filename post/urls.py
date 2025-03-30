from django.urls import path
from . import views

urlpatterns = [
    path('create_post/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/manage-associations/', views.manage_associations, name='manage_associations'),
]