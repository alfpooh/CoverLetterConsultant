# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('submit/', views.submit_request_view, name='submit_request'),
    # Add other URL patterns here...
]