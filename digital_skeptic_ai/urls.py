# Django URL configuration for Digital Skeptic AI
from django.urls import path
from . import views

# URL patterns for the application
urlpatterns = [
    # Root URL pattern (/)
    # Handles POST requests with a 'url' parameter to analyze news articles
    # Returns a PDF report with the critical analysis
    path('', views.process_url, name='process_url'),
]