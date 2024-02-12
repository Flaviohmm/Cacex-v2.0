from django.shortcuts import render
from plataforma.models import RegistroFuncionarios, Status, Setor, Atividade
from django.db.models import Count


def grafico_geral(request):
    registros = RegistroFuncionarios.objects.all()
    status_total = (
        registros.filter(status=Status.CONCLUIDO).count() + 
        registros.filter(status=Status.EM_ANALISE).count() +
        registros.filter(status=Status.NAO_INICIADO).count() +
        registros.filter(status=Status.PENDENTE).count() +
        registros.filter(status=Status.SUSPENSO).count()
    )

    registros_concluidos = RegistroFuncionarios.objects.filter(status=Status.CONCLUIDO).count()

    registros_pendentes = registros.filter(status=Status.PENDENTE).count() 

    registros_em_analises = registros.filter(status=Status.EM_ANALISE).count()

    registros_nao_iniciados = registros.filter(status=Status.NAO_INICIADO).count()

    registros_suspensos = registros.filter(status=Status.SUSPENSO).count()

    orgaos_setores = Setor.objects.all()

    atividades = Atividade.objects.all()

    # Recupere a contagem de registros para cada orgao_setor
    contagem_por_orgao_setor = RegistroFuncionarios.objects.values('orgao_setor__orgao_setor').annotate(contagem=Count('orgao_setor'))

    # Transforme os resultados em listas separadas
    orgaos_setor_labels = [item['orgao_setor__orgao_setor'] for item in contagem_por_orgao_setor]
    contagem_registros = [item['contagem'] for item in contagem_por_orgao_setor]

    # Recupere a contagem de registros para cada atividade
    contagem_por_atividade = RegistroFuncionarios.objects.values('atividade__atividade').annotate(contagem=Count('atividade'))

    # Transforme os resultados em listas separadas
    atividades_labels = [item['atividade__atividade'] for item in contagem_por_atividade]
    contagem_atividades = [item['contagem'] for item in contagem_por_atividade]

    print(atividades_labels)
    print(contagem_atividades)

    context = {
        'orgaos_setores': orgaos_setores,
        'registros': registros,
        'status_total': status_total,
        'registros_concluidos': registros_concluidos,
        'registros_pendentes': registros_pendentes,
        'registros_em_analises': registros_em_analises,
        'registros_nao_iniciados': registros_nao_iniciados,
        'registros_suspensos': registros_suspensos,
        'orgaos_setor_labels': orgaos_setor_labels,
        'contagem_registros': contagem_registros,
        'atividades_labels': atividades_labels,
        'contagem_atividades': contagem_atividades,
    }

    return render(request, 'tb_geral.html', context)

