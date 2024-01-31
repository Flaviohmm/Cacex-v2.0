from django.urls import path
from . import views


urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.inicio, name='inicio'),
    path('adicionar_registro/', views.adicionar_registro, name='adicionar_registro'),
    path('adicionar_registro_rf/', views.adicionar_registro_rf, name='adicionar_registro_rf'),
    path('adicionar_registro_fgts_ind_con/', views.adicionar_registro_fgts_ind_con, name='adicionar_registro_fgts_ind_con'),
    path('adicionar_nome/', views.adicionar_nome, name='adicionar_nome'),
    path('adicionar_orgao_setor/', views.adicionar_orgao_setor, name='adicionar_orgao_setor'),
    path('adicionar_municipio/', views.adicionar_municipio, name='adicionar_municipio'),
    path('adicionar_atividade/', views.adicionar_atividade, name='adicionar_atividade'),
    path('visualizar_tabela/', views.visualizar_tabela, name='visualizar_tabela'),
    path('visualizar_tabela_rf/', views.visualizar_tabela_rf, name='visualizar_tabela_rf'),
    path('visualizar_tabela_fic/', views.visualizar_tabela_fic, name='visualizar_tabela_fic'),
    path('tabela_filtrada/', views.tabela_filtrada, name='tabela_filtrada'),
    path('tabela_caixa/', views.tabela_caixa, name='tabela_caixa'),
    path('tabela_estado/', views.tabela_estado, name='tabela_estado'),
    path('tabela_fnde/', views.tabela_fnde, name='tabela_fnde'),
    path('tabela_simec/', views.tabela_simec, name='tabela_simec'),
    path('tabela_fns/', views.tabela_fns, name='tabela_fns'),
    path('tabela_entidade/', views.tabela_entidade, name='tabela_entidade'),
    path('tabela_filtrada_caixa/', views.tabela_filtrada_caixa, name='tabela_filtrada_caixa'),
    path('tabela_filtrada_estado/', views.tabela_filtrada_estado, name='tabela_filtrada_estado'),
    path('tabela_filtrada_fnde/', views.tabela_filtrada_fnde, name='tabela_filtrada_fnde'),
    path('tabela_filtrada_simec/', views.tabela_filtrada_simec, name='tabela_filtrada_simec'),
    path('tabela_filtrada_fns/', views.tabela_filtrada_fns, name='tabela_filtrada_fns'),
    path('tabela_filtrada_entidade/', views.tabela_filtrada_entidade, name='tabela_filtrada_entidade'),
    path('editar_registro/<int:registro_id>/', views.editar_registro, name='editar_registro'),
    path('excluir_registros/<int:registro_id>/', views.excluir_registro, name='excluir_registro'),
    path('historico/', views.historico, name='historico'),
    path('historico_detail/<int:registro_id>/', views.historico_detail, name='historico_detail'),
    path('anexar_registro/<int:registro_id>/', views.anexar_registro, name='anexar_registro'),
    path('desanexar_registro/<int:registro_id>/', views.desanexar_registro, name='desanexar_registro'),
    path('mostrar_registros_anexados/', views.mostrar_registros_anexados, name='mostrar_registros_anexados'),
    
]
