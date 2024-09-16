from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL configuration
    path('', include('myapp.urls')),  # Include the app's URL patterns
]