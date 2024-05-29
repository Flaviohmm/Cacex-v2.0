from django.urls import path
from . import views


urlpatterns = [
    path('grafico_geral/', views.grafico_geral, name='grafico_geral'),
    path('gerador_pdf_tb_geral/', views.gerador_pdf_tb_geral, name='gerador_pdf_tb_geral'),
    path('gerar_pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('gerar_pdf_caixa_municipios_selecionados/', views.gerar_pdf_caixa_municipios_selecionados, name='gerar_pdf_caixa_municipios_selecionados'),
    path('gerar_pdf_tabela_estado/', views.gerar_pdf_tabela_estado, name='gerar_pdf_tabela_estado'),
    path('gerar_pdf_tabela_fnde/', views.gerar_pdf_tabela_fnde, name='gerar_pdf_tabela_fnde'),
    path('gerar_pdf_tabela_simec/', views.gerar_pdf_tabela_simec, name='gerar_pdf_tabela_simec'),
    path('gerar_pdf_tabela_fns/', views.gerar_pdf_tabela_fns, name='gerar_pdf_tabela_fns'),
    path('gerar_pdf_tabela_entidade/', views.gerar_pdf_tabela_entidade, name='gerar_pdf_tabela_entidade'),
]
