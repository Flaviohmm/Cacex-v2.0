from django.urls import path
from . import views


urlpatterns = [
    path('grafico_geral/', views.grafico_geral, name='grafico_geral'),
    path('gerador_pdf_tb_geral/', views.gerador_pdf_tb_geral, name='gerador_pdf_tb_geral'),
]
