from django.urls import path
from . import views


urlpatterns = [
    path('grafico_geral/', views.grafico_geral, name='grafico_geral'),
]
