from django.urls import path
from . import views


urlpatterns = [
    path('grafico_geral/', views.grafico_geral, name='grafico_geral'),
    path('gerador_pdf_tb_geral/', views.gerador_pdf_tb_geral, name='gerador_pdf_tb_geral'),
    path('gerar_pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('gerar_pdf_caixa_municipios_selecionados/', views.gerar_pdf_caixa_municipios_selecionados, name='gerar_pdf_caixa_municipios_selecionados'),
    path('gerar_pdf_tabela_estado/', views.gerar_pdf_tabela_estado, name='gerar_pdf_tabela_estado'),
]
