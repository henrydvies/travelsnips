from django.urls import path
from . import views

urlpatterns = [
    path('create_post/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/manage-associations/', views.manage_associations, name='manage_associations'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/add-subpost/', views.add_subpost, name='add_subpost'),
    path('subpost/<int:subpost_id>/edit/', views.edit_subpost, name='edit_subpost'),
    path('api/post-locations/', views.post_locations, name='post_locations'),
]