from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('adicionar_registro/', views.adicionar_registro, name='adicionar_registro'),
    path('adicionar_nome/', views.adicionar_nome, name='adicionar_nome'),
    path('adicionar_orgao_setor/', views.adicionar_orgao_setor, name='adicionar_orgao_setor'),
    path('adicionar_municipio/', views.adicionar_municipio, name='adicionar_municipio'),
    path('adicionar_atividade/', views.adicionar_atividade, name='adicionar_atividade'),
    path('visualizar_tabela/', views.visualizar_tabela, name='visualizar_tabela')
]
