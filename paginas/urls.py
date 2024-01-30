from django.urls import path
from . import views


urlpatterns = [
    path('base_admin/', views.base_admin, name='base_admin'),
]
