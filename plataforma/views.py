from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RegistroFuncionarios, Nome, Setor, Municipio, Atividade, Status
from .utils import calcular_valores, exibir_modal_prazo_vigencia, dia_trabalho_total
import locale


@login_required(login_url='/auth/login')
def home(request):
    registros = RegistroFuncionarios.objects.all()
    return render(request, 'home.html', {'registros': registros})

def adicionar_nome(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        Nome.objects.create(nome=nome)
        return redirect('home')
    
    return render(request, 'adicionar_nome.html')

def adicionar_orgao_setor(request):
    if request.method == 'POST':
        orgao_setor = request.POST.get('orgao_setor')
        Setor.objects.create(orgao_setor=orgao_setor)
        return redirect('home')
    
    return render(request, 'adicionar_orgao_setor.html')

def adicionar_municipio(request):
    if request.method == 'POST':
        municipio = request.POST.get('municipio')
        Municipio.objects.create(municipio=municipio)
        return redirect('home')
    
    return render(request, 'adicionar_municipio.html')

def adicionar_atividade(request):
    if request.method == 'POST':
        atividade = request.POST.get('atividade')
        Atividade.objects.create(atividade=atividade)
        return redirect('home')
    
    return render(request, 'adicionar_atividade.html')

def adicionar_registro(request):
    # Defina a localidade para o formato brasileiro
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    if request.method == 'POST':
        nome = Nome.objects.get(id=request.POST.get('nome'))
        orgao_setor = Setor.objects.get(id=request.POST.get('orgao_setor'))
        municipio = Municipio.objects.get(id=request.POST.get('municipio'))
        atividade = Atividade.objects.get(id=request.POST.get('atividade'))
        num_convenio = request.POST.get('num_convenio')
        parlamentar = request.POST.get('parlamentar')
        objeto = request.POST.get('objeto')
        oge_ogu = float(request.POST.get('oge_ogu'))
        cp_prefeitura = float(request.POST.get('cp_prefeitura'))
        valor_liberado = float(request.POST.get('valor_liberado'))
        prazo_vigencia = request.POST.get('prazo_vigencia')
        situacao = request.POST.get('situacao')
        providencia = request.POST.get('providencia')
        data_recepcao = request.POST.get('data_recepcao')
        data_inicio = request.POST.get('data_inicio')
        documento_pendente = 'documento_pendente' in request.POST
        documento_cancelado = 'documento_cancelado' in request.POST
        data_fim = request.POST.get('data_fim')

        # Crie instâncias dos modelos relacionados...
        registro = RegistroFuncionarios(
            nome=nome,
            orgao_setor=orgao_setor,
            municipio=municipio,
            atividade=atividade,
            num_convenio=num_convenio,
            parlamentar=parlamentar,
            objeto=objeto,
            oge_ogu=oge_ogu,
            cp_prefeitura=cp_prefeitura,
            valor_liberado=valor_liberado,
            prazo_vigencia=prazo_vigencia,
            situacao=situacao,
            providencia=providencia,
            data_recepcao=data_recepcao,
            data_inicio=data_inicio,
            documento_pendente=documento_pendente,
            documento_cancelado=documento_cancelado,
            data_fim=data_fim,
        )

        # Salve o registro
        registro.save()

        # Chame as funções utilitárias
        registro.valor_total, registro.falta_liberar = calcular_valores(registro)
        exibir_modal, dias_restantes = exibir_modal_prazo_vigencia(registro)
        registro.duracao_dias_uteis = dia_trabalho_total(registro.data_inicio, registro.data_fim)

        # Formate os valores usando a localidade definida
        registro.oge_ogu = locale.currency(oge_ogu, grouping=True)
        registro.cp_prefeitura = locale.currency(cp_prefeitura, grouping=True)
        registro.valor_liberado = locale.currency(valor_liberado, grouping=True)
        registro.valor_total = locale.currency(registro.valor_total, grouping=True)
        registro.falta_liberar = locale.currency(registro.falta_liberar, grouping=True)

        return redirect('home')
    
    # Recupere as opções para os campos estrangeiros...
    nomes = Nome.objects.all()
    setores = Setor.objects.all()
    municipios = Municipio.objects.all()
    atividades = Atividade.objects.all()
    registros = RegistroFuncionarios.objects.all()

    context = {
        'nomes': nomes,
        'setores': setores,
        'municipios': municipios,
        'atividades': atividades,
        'messages': messages.get_messages(request),
        'registros': registros,
    }

    return render(request, 'adicionar_registro.html', context)

def visualizar_tabela(request):
    registros = RegistroFuncionarios.objects.all()

    return render(request, 'visualizar_tabela.html', {'registros': registros})