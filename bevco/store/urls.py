from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_phone, name='login_phone'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('buy/<int:product_id>/', views.buy, name='buy'),
    path('success/', views.payment_success, name='payment_success'),
]
