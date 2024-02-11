from django.shortcuts import render
from plataforma.models import RegistroFuncionarios, Status


def base_admin(request):
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

    context = {
        'registros': registros,
        'status_total': status_total,
        'registros_concluidos': registros_concluidos,
        'registros_pendentes': registros_pendentes,
        'registros_em_analises': registros_em_analises,
        'registros_nao_iniciados': registros_nao_iniciados,
        'registros_suspensos': registros_suspensos,
    }

    return render(request, 'tb_geral.html', context)
