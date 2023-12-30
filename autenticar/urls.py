from django.urls import path
from . import views


urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('sair/', views.sair, name='sair'),
    path('password_reset_request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset/confirm/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
