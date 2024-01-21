from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from django.utils import timezone
from .models import RegistroFuncionarios, Nome, Setor, Municipio, Atividade, Historico
from .utils import calcular_valores, exibir_modal_prazo_vigencia, dia_trabalho_total
import locale
import json


@login_required(login_url='/auth/login')
def home(request):
    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Recupere todos os registros
    registros = RegistroFuncionarios.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'home.html', context)

@login_required(login_url='/auth/login')
def inicio(request):
    return render(request, 'inicio.html')

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

        # Configure a localidade para o formato brasileiro
        locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

        # Remova caracteres não numéricos da string e converta para float
        oge_ogu_str = request.POST.get('oge_ogu')
        oge_ogu_limpo = ''.join(c for c in oge_ogu_str if c.isdigit() or c == '.' or c == ',')
        oge_ogu = locale.atof(oge_ogu_limpo)

        # Repita o processo para outros campos que podem ter formato monetário
        cp_prefeitura_str = request.POST.get('cp_prefeitura')
        cp_prefeitura_limpo = ''.join(c for c in cp_prefeitura_str if c.isdigit() or c == '.' or c == ',')
        cp_prefeitura = locale.atof(cp_prefeitura_limpo)

        valor_liberado_str = request.POST.get('valor_liberado')
        valor_liberado_limpo = ''.join(c for c in valor_liberado_str if c.isdigit() or c == '.' or c == ',')
        valor_liberado = locale.atof(valor_liberado_limpo)

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
    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Recupere todos os registros
    registros = RegistroFuncionarios.objects.all()

    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros': registros,
    }

    # Renderize o modelo com o contexto
    return render(request, 'visualizar_tabela.html', context)

def editar_registro(request, registro_id):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Obtenha a instância do registro a ser editado
    registro = get_object_or_404(RegistroFuncionarios, id=registro_id)

    # Chame as funções utilitárias
    registro.valor_total, registro.falta_liberar = calcular_valores(registro)
    exibir_modal, dias_restantes = exibir_modal_prazo_vigencia(registro)
    registro.duracao_dias_uteis = dia_trabalho_total(registro.data_inicio, registro.data_fim)

    # Obtenha os dados anteriores fora do bloco condicional
    dados_anteriores = {
        'nome': registro.nome.nome,
        'orgao_setor': registro.orgao_setor.orgao_setor,
        'municipio': registro.municipio.municipio,
        'atividade': registro.atividade.atividade,
        'num_convenio': registro.num_convenio,
        'parlamentar': registro.parlamentar,
        'objeto': registro.objeto,
        'oge_ogu': locale.currency(registro.oge_ogu, grouping=True),
        'cp_prefeitura': locale.currency(registro.cp_prefeitura, grouping=True),
        'valor_total': locale.currency(registro.valor_total, grouping=True),
        'valor_liberado': locale.currency(registro.valor_liberado, grouping=True),
        'falta_liberar': locale.currency(registro.falta_liberar, grouping=True),
        'prazo_de_vigencia': registro.prazo_vigencia,
        'situacao': registro.situacao,
        'providencia': registro.providencia,
        'data_recepcao': registro.data_recepcao,
        'data_inicio': registro.data_inicio,
        'documento_pendente': registro.documento_pendente,
        'documento_cancelado': registro.documento_cancelado,
        'data_fim': registro.data_fim,
        'duracao_dias_uteis': registro.duracao_dias_uteis,
    }

    if request.method == 'POST':
        # Atualize os campos do registro com os dados do POST
        registro.nome = Nome.objects.get(id=request.POST.get('nome'))
        registro.orgao_setor = Setor.objects.get(id=request.POST.get('orgao_setor'))
        registro.municipio = Municipio.objects.get(id=request.POST.get('municipio'))
        registro.atividade = Atividade.objects.get(id=request.POST.get('atividade'))
        registro.num_convenio = request.POST.get('num_convenio')
        registro.parlamentar = request.POST.get('parlamentar')
        registro.objeto = request.POST.get('objeto')

        # Configure a localidade para o formato brasileiro
        locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

        # Remova caracteres não numéricos da string e converta para float
        oge_ogu_str = request.POST.get('oge_ogu')
        oge_ogu_limpo = ''.join(c for c in oge_ogu_str if c.isdigit() or c == '.' or c == ',')
        registro.oge_ogu = locale.atof(oge_ogu_limpo)

        # Repita o processo para os outros campos que podem ter formato monetário
        cp_prefeitura_str = request.POST.get('cp_prefeitura')
        cp_prefeitura_limpo = ''.join(c for c in cp_prefeitura_str if c.isdigit() or c == '.' or c == ',')
        registro.cp_prefeitura = locale.atof(cp_prefeitura_limpo)

        valor_liberado_str = request.POST.get('valor_liberado')
        valor_liberado_limpo = ''.join(c for c in valor_liberado_str if c.isdigit() or c == '.' or c == ',')
        registro.valor_liberado = locale.atof(valor_liberado_limpo)

        registro.prazo_vigencia = request.POST.get('prazo_vigencia')
        registro.situacao = request.POST.get('situacao')
        registro.providencia = request.POST.get('providencia')
        registro.data_recepcao = request.POST.get('data_recepcao')
        registro.data_inicio = request.POST.get('data_inicio')
        registro.documento_pendente = 'documento_pendente' in request.POST
        registro.documento_cancelado = 'documento_cancelado' in request.POST
        registro.data_fim = request.POST.get('data_fim')

        # Salve o registro
        registro.save()

        # Registre a atividade no histórico, incluindo os dados anteriores
        Historico.objects.create(
            usuario=request.user,
            acao='editar',
            dados_anteriores=dados_anteriores,
            data=timezone.now(),
            registro=registro
        )

        # Chame as funções utilitárias
        registro.valor_total, registro.falta_liberar = calcular_valores(registro)
        exibir_modal, dias_restantes = exibir_modal_prazo_vigencia(registro)
        registro.duracao_dias_uteis = dia_trabalho_total(registro.data_inicio, registro.data_fim)

        # Formate os valores usando a localidade definida
        registro.oge_ogu = locale.currency(registro.oge_ogu, grouping=True)
        registro.cp_prefeitura = locale.currency(registro.cp_prefeitura, grouping=True)
        registro.valor_liberado = locale.currency(registro.valor_liberado, grouping=True)
        registro.valor_total = locale.currency(registro.valor_total, grouping=True)
        registro.falta_liberar = locale.currency(registro.falta_liberar, grouping=True)
        
        messages.add_message(request, constants.SUCCESS, 'Registro editado com sucesso.')
        messages.success(request, 'Registro editado com sucesso.')
        return redirect('home')
    
    # Consulte o histórico
    historico_registros = Historico.objects.filter(registro=registro).order_by('-data')

    # Exiba ou manipule os dados anteriores conforme necessário
    for historico in historico_registros:
        dados_anteriores = historico.dados_anteriores
    
    # Recupere as opções para os campos estrangeiros...
    nomes = Nome.objects.all()
    setores = Setor.objects.all()
    municipios = Municipio.objects.all()
    atividades = Atividade.objects.all()
    registros = RegistroFuncionarios.objects.all()

    context = {
        'registro': registro,
        'nomes': nomes,
        'setores': setores,
        'municipios': municipios,
        'atividades': atividades,
        'messages': messages.get_messages(request),
        'registros': registros,
        'historico_registros': historico_registros,
    }

    return render(request, 'editar_registro.html', context)

def excluir_registro(request, registro_id):
    try:
        # Busque o registro pelo ID
        registro = RegistroFuncionarios.objects.get(id=registro_id)

        # Exclua o registro
        registro.delete()

        messages.success(request, 'Registro excluido com sucesso.')
    except RegistroFuncionarios.DoesNotExist:
        messages.error(request, 'Registro não encontrado.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao excluir o registro: {e}')

    return redirect('home')

def tabela_filtrada(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    nome_id = request.GET.get('nome')
    orgao_setor_id = request.GET.get('orgao_setor')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.all()

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)
    
    if orgao_setor_id:
        registros_filtrados = registros_filtrados.filter(orgao_setor__id=orgao_setor_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada.html', context)

def historico(request):
    historico_registros = Historico.objects.all()

    context = {
        'historico_registros': historico_registros
    }

    return render(request, 'historico_template.html', context)

def tabela_caixa(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='CAIXA')

    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'tabela_caixa.html', context)

def tabela_filtrada_caixa(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Adicionando o filtro para orgao_setor igual a 'CAIXA'
    orgao_setor_caixa = Setor.objects.get(orgao_setor='CAIXA')

    nome_id = request.GET.get('nome')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_caixa)

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada_caixa.html', context)

def tabela_estado(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='ESTADO')

    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'tabela_estado.html', context)

def tabela_filtrada_estado(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Adicionando o filtro para orgao_setor igual a 'ESTADO'
    orgao_setor_estado = Setor.objects.get(orgao_setor='ESTADO')

    nome_id = request.GET.get('nome')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_estado)

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada_estado.html', context)

def tabela_fnde(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='FNDE')

    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'tabela_fnde.html', context)

def tabela_filtrada_fnde(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Adicionando o filtro para orgao_setor igual a 'FNDE'
    orgao_setor_fnde = Setor.objects.get(orgao_setor='FNDE')

    nome_id = request.GET.get('nome')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_fnde)

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada_fnde.html', context)

def tabela_simec(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='SIMEC')

    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'tabela_simec.html', context)

def tabela_filtrada_simec(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Adicionando o filtro para orgao_setor igual a 'SIMEC'
    orgao_setor_simec = Setor.objects.get(orgao_setor='SIMEC')

    nome_id = request.GET.get('nome')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_simec)

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada_simec.html', context)

def tabela_fns(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='FNS')

    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'tabela_fns.html', context)

def tabela_filtrada_fns(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Adicionando o filtro para orgao_setor igual a 'FNS'
    orgao_setor_fns = Setor.objects.get(orgao_setor='FNS')

    nome_id = request.GET.get('nome')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_fns)

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada_fns.html', context)

def tabela_entidade(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='Entidade')

    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    
    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'tabela_entidade.html', context)

def tabela_filtrada_entidade(request):
    nomes = Nome.objects.all()
    orgaos_setores = Setor.objects.all()
    municipios = Municipio.objects.all()

    # Adicionando o filtro para orgao_setor igual a 'Entidade'
    orgao_setor_entidade = Setor.objects.get(orgao_setor='Entidade')

    nome_id = request.GET.get('nome')
    municipio_id = request.GET.get('municipio')
    num_convenio = request.GET.get('num_convenio')
    parlamentar = request.GET.get('parlamentar')
    prazo_vigencia = request.GET.get('prazo_vigencia')
    status = request.GET.get('status')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_entidade)

    if nome_id:
        registros_filtrados = registros_filtrados.filter(nome__id=nome_id)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    if num_convenio:
        registros_filtrados = registros_filtrados.filter(num_convenio__icontains=num_convenio)

    if parlamentar:
        registros_filtrados = registros_filtrados.filter(parlamentar__icontains=parlamentar)

    if prazo_vigencia:
        registros_filtrados = registros_filtrados.filter(prazo_vigencia__icontains=prazo_vigencia)

    if status:
        registros_filtrados = registros_filtrados.filter(status__icontains=status)

    context = {
        'nomes': nomes,
        'orgaos_setores': orgaos_setores,
        'municipios': municipios,
        'registros_filtrados': registros_filtrados,
    }

    return render(request, 'tabela_filtrada_entidade.html', context)
