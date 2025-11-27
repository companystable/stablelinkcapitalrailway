from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('test-email/', views.test_email, name='test-email'),
  
]
