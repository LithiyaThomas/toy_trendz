from django.urls import path
from . import views

#app_name = 'accounts'

urlpatterns = [
    path('user-login', views.user_login, name='user_login'),
    path('user-register', views.user_register, name='user_register'),
    path('verify-otp', views.verify_otp, name='verify_otp'),
    path('resend-otp', views.resend_otp, name='resend_otp'),  # Added the path for resend_otp
    path('', views.home, name='home'),
]
