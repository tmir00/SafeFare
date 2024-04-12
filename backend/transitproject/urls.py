"""transitproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from transitapp.views import UserRegistrationView, UserDetailView, PasswordRecoveryView, LoginView, CreateStripeCustomerView, HandlePaymentView
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('recover/', PasswordRecoveryView.as_view(), name='password-recover'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('payments/setup/', CreateStripeCustomerView.as_view(), name='create-stripe-customer'),
    path('payments/pay/', HandlePaymentView.as_view(), name='make-payment')
]
