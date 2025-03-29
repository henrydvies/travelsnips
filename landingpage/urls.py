from django.urls import path
from . import views

urlpatterns = [
    path('landingpage', views.landing_view, name='landingpage'),
]