from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from datetime import datetime
from .models import (
    RegistroFuncionarios, 
    Nome, 
    Setor, 
    Municipio, 
    Atividade, 
    Historico,
    RegistroReceitaFederal,
    RegistroFGTSIndCon,
    RegistroAdminstracao,
)
from .utils import calcular_valores, exibir_modal_prazo_vigencia, dia_trabalho_total
from .templatetags.custom_filters import format_currency
import re


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

def adicionar(request):
    return render(request, 'adicionar.html')

def adicionar_dados(request):
    return render(request, 'adicionar_dados.html')

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

def listar_classes_adicionadas():
    classes_adicionadas = {
        'nomes': Nome.objects.all(),
        'setores': Setor.objects.all(),
        'municipios': Municipio.objects.all(),
        'atividades': Atividade.objects.all(),
    }

    return classes_adicionadas

def listar_dados(request):
    # Chame a função para obter os objetos adicionados
    classes_adicionadas = listar_classes_adicionadas()

    # Acesse os objetos de cada classe conforme necessário
    nomes = classes_adicionadas['nomes']
    setores = classes_adicionadas['setores']
    municipios = classes_adicionadas['municipios']
    atividades = classes_adicionadas['atividades']

    if request.method == 'POST':
        #Verifica se o formulário foi submetido para edição
        if 'editar_nome' in request.POST:
            nome_id = request.POST.get('editar_nome')
            nome = get_object_or_404(Nome, id=nome_id)
            novo_nome = request.POST.get('novo_nome')
            nome.nome = novo_nome
            nome.save()
        elif 'excluir_nome' in request.POST:
            nome_id = request.POST.get('excluir_nome')
            nome = get_object_or_404(Nome, id=nome_id)
            nome.delete()
        elif 'editar_setor' in request.POST:
            setor_id = request.POST.get('editar_setor')
            setor = get_object_or_404(Setor, id=setor_id)
            novo_setor = request.POST.get('novo_setor')
            setor.orgao_setor = novo_setor
            setor.save()
        elif 'excluir_setor' in request.POST:
            setor_id = request.POST.get('excluir_setor')
            setor = get_object_or_404(Setor, id=setor_id)
            setor.delete()
        elif 'editar_municipio' in request.POST:
            municipio_id = request.POST.get('editar_municipio')
            municipio = get_object_or_404(Municipio, id=municipio_id)
            novo_municipio = request.POST.get('novo_municipio')
            municipio.municipio = novo_municipio
            municipio.save()
        elif 'excluir_municipio' in request.POST:
            municipio_id = request.POST.get('excluir_municipio')
            municipio = get_object_or_404(Municipio, id=municipio_id)
            municipio.delete()
        elif 'editar_atividade' in request.POST:
            atividade_id = request.POST.get('editar_atividade')
            atividade = get_object_or_404(Atividade, id=atividade_id)
            nova_atividade = request.POST.get('nova_atividade')
            atividade.atividade = nova_atividade
            atividade.save()
        elif 'excluir_atividade' in request.POST:
            atividade_id = request.POST.get('excluir_atividade')
            atividade = get_object_or_404(Atividade, id=atividade_id)
            atividade.delete()

        return redirect('listar_dados')

    context = {
        'nomes': nomes,
        'setores': setores,
        'municipios': municipios,
        'atividades': atividades,
        'classes_adicionadas': classes_adicionadas,
    }
    return render(request, 'listar_dados.html', context)

def adicionar_registro(request):
    if request.method == 'POST':
        nome = Nome.objects.get(id=request.POST.get('nome'))
        orgao_setor = Setor.objects.get(id=request.POST.get('orgao_setor'))
        municipio = Municipio.objects.get(id=request.POST.get('municipio'))
        atividade = Atividade.objects.get(id=request.POST.get('atividade'))
        num_convenio = request.POST.get('num_convenio')
        parlamentar = request.POST.get('parlamentar')
        objeto = request.POST.get('objeto')

        # Remova caracteres de formatação do valor recuperado
        oge_ogu_str = request.POST.get('oge_ogu', 0).replace('R$', '').replace('.', '').replace(',', '.')
        oge_ogu = float(oge_ogu_str)
        
        cp_prefeitura_str = request.POST.get('cp_prefeitura', 0).replace('R$', '').replace('.', '').replace(',', '.')
        cp_prefeitura = float(cp_prefeitura_str)

        valor_liberado_str = request.POST.get('valor_liberado', 0).replace('R$', '').replace('.', '').replace(',', '.')
        valor_liberado = float(valor_liberado_str)

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

        # Formate os valores manualmente como moeda (considerando o formato brasileiro)
        registro.oge_ogu = f'R${oge_ogu:,.2f}'
        registro.cp_prefeitura = f'R${cp_prefeitura:,.2f}'
        registro.valor_liberado = f'R${valor_liberado:,.2f}'
        registro.valor_total = f'R${registro.valor_total:,.2f}'
        registro.falta_liberar = f'R${registro.falta_liberar:,.2f}'

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

def dados_atuais_registro(registro):
    dados_atuais = {
        'nome': registro.nome.nome,
        'orgao_setor': registro.orgao_setor.orgao_setor,
        'municipio': registro.municipio.municipio,
        'atividade': registro.atividade.atividade,
        'num_convenio': registro.num_convenio,
        'parlamentar': registro.parlamentar,
        'objeto': registro.objeto,
        'oge_ogu': format_currency(registro.oge_ogu),
        'cp_prefeitura': format_currency(registro.cp_prefeitura),
        'valor_total': format_currency(registro.valor_total),
        'valor_liberado': format_currency(registro.valor_liberado),
        'falta_liberar': format_currency(registro.falta_liberar),
        'prazo_vigencia': registro.prazo_vigencia.strftime("%d/%m/%Y"),
        'situacao': registro.situacao,
        'providencia': registro.providencia,
        'status': registro.status,
        'data_recepcao': registro.data_recepcao.strftime("%d/%m/%Y"),
        'data_inicio': registro.data_inicio.strftime("%d/%m/%Y") if registro.data_inicio else "",
        'documento_pendente': 'Sim' if registro.documento_pendente else 'Não',
        'documento_cancelado': 'Sim' if registro.documento_cancelado else 'Não',
        'data_fim': registro.data_fim.strftime("%d/%m/%Y") if registro.data_fim else "",
        'duracao_dias_uteis': registro.duracao_dias_uteis
    }

    return dados_atuais

def comparar_valores(historico_dados_anteriores, historico_dados_atuais):
    diff = []
    for key, value_anterior in historico_dados_anteriores.items():
        if key in historico_dados_atuais:
            value_atual = historico_dados_atuais[key]
            if value_atual != value_anterior:
                diff.append((key, value_anterior, value_atual))
    return diff

def editar_registro(request, registro_id):
    # Obtenha a instância do registro a ser editado
    registro = get_object_or_404(RegistroFuncionarios, id=registro_id)

    # Consulte o histórico
    historico_registros = Historico.objects.filter(registro=registro).order_by('-data')

    # Chame as funções utilitárias
    registro.valor_total, registro.falta_liberar = calcular_valores(registro)
    exibir_modal, dias_restantes = exibir_modal_prazo_vigencia(registro)
    registro.duracao_dias_uteis = dia_trabalho_total(registro.data_inicio, registro.data_fim)

    # Obtenha os dados atuais do registro antes de qualquer alteração
    dados_atuais = dados_atuais_registro(registro)



    if request.method == 'POST':
        # Guarde os dados atuais antes das alterações
        dados_anteriores = dados_atuais

        # Exiba ou manipule os dados anteriores conforme necessário
        for historico in historico_registros:
            historico.dados_anteriores = dados_anteriores

        # Atualize os campos do registro com os dados do POST
        registro.nome = Nome.objects.get(id=request.POST.get('nome'))
        registro.orgao_setor = Setor.objects.get(id=request.POST.get('orgao_setor'))
        registro.municipio = Municipio.objects.get(id=request.POST.get('municipio'))
        registro.atividade = Atividade.objects.get(id=request.POST.get('atividade'))
        registro.num_convenio = request.POST.get('num_convenio')
        registro.parlamentar = request.POST.get('parlamentar')
        registro.objeto = request.POST.get('objeto')

        # Remova caracteres de formatação do valor recuperado
        oge_ogu_str = request.POST.get('oge_ogu', 0).replace('R$', '').replace('.', '').replace(',', '.')
        registro.oge_ogu = float(oge_ogu_str)
        
        cp_prefeitura_str = request.POST.get('cp_prefeitura', 0).replace('R$', '').replace('.', '').replace(',', '.')
        registro.cp_prefeitura = float(cp_prefeitura_str)

        valor_liberado_str = request.POST.get('valor_liberado', 0).replace('R$', '').replace('.', '').replace(',', '.')
        registro.valor_liberado = float(valor_liberado_str)

        prazo_vigencia_str = request.POST.get('prazo_vigencia')
        prazo_vigencia = datetime.strptime(prazo_vigencia_str, '%Y-%m-%d')

        registro.prazo_vigencia = prazo_vigencia
        registro.situacao = request.POST.get('situacao')
        registro.providencia = request.POST.get('providencia')

        data_recepcao_str = request.POST.get('data_recepcao')
        data_recepcao = datetime.strptime(data_recepcao_str, '%Y-%m-%d')

        registro.data_recepcao = data_recepcao

        data_inicio_str = request.POST.get('data_inicio')
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')

        registro.data_inicio = data_inicio

        registro.documento_pendente = 'documento_pendente' in request.POST
        registro.documento_cancelado = 'documento_cancelado' in request.POST

        data_fim_str = request.POST.get('data_fim')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')

        registro.data_fim = data_fim

        # Salve o registro
        registro.save()

        
        # Registre a atividade no histórico, incluindo os dados anteriores
        Historico.objects.create(
            usuario=request.user,
            acao='editar',
            dados_anteriores=dados_anteriores,
            dados_atuais=dados_atuais_registro(registro),
            dados_alterados=comparar_valores(dados_anteriores, dados_atuais),
            data=timezone.now(),
            registro=registro
        )

        for historico in historico_registros:
            historico.dados_atuais = dados_atuais_registro(registro)

        # Chame as funções utilitárias
        registro.valor_total, registro.falta_liberar = calcular_valores(registro)
        exibir_modal, dias_restantes = exibir_modal_prazo_vigencia(registro)
        registro.duracao_dias_uteis = dia_trabalho_total(registro.data_inicio, registro.data_fim)

        # Formate os valores usando a localidade definida
        registro.oge_ogu = f'R${registro.oge_ogu:,.2f}'
        registro.cp_prefeitura = f'R${registro.cp_prefeitura:,.2f}'
        registro.valor_liberado = f'R${registro.valor_liberado:,.2f}'
        registro.valor_total = f'R${registro.valor_total:,.2f}'
        registro.falta_liberar = f'R${registro.falta_liberar:,.2f}'
        
        messages.add_message(request, constants.SUCCESS, 'Registro editado com sucesso.')
        messages.success(request, 'Registro editado com sucesso.')
        return redirect('home')
    
    
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

    # Inicializa a lista de diferenças como vazia
    registros = []

    for hist in historico_registros:
        registro = {
            'acao': hist.acao,
            'data': hist.data,
            'usuario': hist.usuario,
            'dados_anteriores': hist.dados_anteriores,
            'dados_atuais': hist.dados_atuais,
            'dados_alterados': comparar_valores(hist.dados_anteriores, hist.dados_atuais),
        }
        registros.append(registro)
        print(comparar_valores(hist.dados_atuais, hist.dados_anteriores))

    context = {
        'historico_registros': registros,
        
    }

    return render(request, 'historico_template.html', context)

def historico_detail(request, registro_id):
    # Obtenha o registro específico ou retorne um 404 se não existir
    registro = get_object_or_404(RegistroFuncionarios, id=registro_id)

    # Obtém os registros do histórico relacionados ao registro específico
    historico_registros = Historico.objects.filter(registro_id=registro).order_by('-data')

    # Inicializa a lista de diferenças como vazia
    registros = []

    for hist in historico_registros:
        reg = {
            'acao': hist.acao,
            'data': hist.data,
            'usuario': hist.usuario,
            'dados_anteriores': hist.dados_anteriores,
            'dados_atuais': hist.dados_atuais,
            'dados_alterados': comparar_valores(hist.dados_anteriores, hist.dados_atuais)
        }
        registros.append(reg)

    context = {
        'historico_registros': registros,
        'registro_id': registro_id,
    }

    return render(request, 'historico_detail_template.html', context)

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

    return render(request, 'tabela_caixa2.html', context)

def selecionar_municipio(request, municipio_id):
    municipio = Municipio.objects.get(id=municipio_id)
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='CAIXA', municipio=municipio)

    # Recupre dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()

    # Exemplo de operações com o município selecionado
    informacoes = {
        'registros': registros,
        'municipio': municipio,
        'nomes': nomes,
        'municipios': municipios,
    }

    return render(request, 'tabela_caixa.html', informacoes)

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

def anexar_registro(request, registro_id):
    # Obtenha o registro a ser anexado
    registro = get_object_or_404(RegistroFuncionarios, id=registro_id)

    # Obtenha a lista de registros anexados e desanexados da sessão
    registros_anexados = request.session.get('registros_anexados', [])
    registros_desanexados = request.session.get('registros_desanexados', [])

    # Verifique se o registro já está anexado
    if registro_id not in registros_anexados:
        # Chame as funções utilitárias
        registro.valor_total, registro.falta_liberar = calcular_valores(registro)
        registro.duracao_dias_uteis = dia_trabalho_total(registro.data_inicio, registro.data_fim)

        # Converta o registro para um dicionário antes de adicionar à lista
        registro_dict = {
            'id': registro.id,
            'nome': registro.nome.nome,
            'orgao_setor': registro.orgao_setor.orgao_setor,
            'municipio': registro.municipio.municipio,
            'atividade': registro.atividade.atividade,
            'num_convenio': registro.num_convenio,
            'parlamentar': registro.parlamentar,
            'objeto': registro.objeto,
            'oge_ogu': f'R${registro.oge_ogu:,.2f}',
            'cp_prefeitura': f'R${registro.cp_prefeitura:,.2f}',
            'valor_total': f'R${registro.valor_total:,.2f}',
            'valor_liberado': f'R${registro.valor_liberado}',
            'falta_liberar': f'R${registro.falta_liberar:,.2f}',
            'prazo_de_vigencia': registro.prazo_vigencia.strftime('%d-%m-%Y'),
            'situacao': registro.situacao,
            'providencia': registro.providencia,
            'status': registro.status,
            'data_recepcao': registro.data_recepcao.strftime('%d-%m-%Y'),
            'data_inicio': registro.data_inicio.strftime('%d-%m-%Y') if registro.data_inicio else None,
            'documento_pendente': registro.documento_pendente,
            'documento_cancelado': registro.documento_cancelado,
            'data_fim': registro.data_fim.strftime('%d-%m-%Y') if registro.data_fim else None,
            'duracao_dias_uteis': registro.duracao_dias_uteis,
        }

        # Adicione o registro completo à lista de registros anexados
        registros_anexados.append(registro_dict)

        # Remova o registro da lista de registros desanexadas, se estiver presente
        if registro_id in registros_desanexados:
            registros_desanexados.remove(registro_id)

        # Atualize a lista de registros anexados e desanexados na sessão
        request.session['registros_anexados'] = registros_anexados
        request.session['registros_desanexados'] = registros_desanexados

        # Remova o registro da tabela original
        registro.delete()

    # Redirecione para a página que mostrará todos os registros anexados
    return redirect('mostrar_registros_anexados')

def desanexar_registro(request, registro_id):
    # Obtenha a lista de registros anexados e desanexados da sessão
    registros_anexados = request.session.get('registros_anexados', [])
    registros_desanexados = request.session.get('registros_desanexados', [])

    # Verifique se o registro já está desanexado
    if registro_id not in registros_desanexados:
        # Obtenha o registro a ser desanexado a partir da lista de registros anexados
        registro_dict = next((registro for registro in registros_anexados if registro['id'] == registro_id), None)

        if registro_dict:
            # Crie uma instância de Nome (substitua 'Nome' pelo seu modelo real)
            nome_instance = Nome.objects.get(nome=registro_dict['nome'])
            orgao_setor_instance = Setor.objects.get(orgao_setor=registro_dict['orgao_setor'])
            municipio_instance = Municipio.objects.get(municipio=registro_dict['municipio'])
            atividade_instance = Atividade.objects.get(atividade=registro_dict['atividade'])

            # Converta o registro_dict para um objeto RegistroFuncionarios
            novo_registro = RegistroFuncionarios(
                nome=nome_instance,
                orgao_setor=orgao_setor_instance,
                municipio=municipio_instance,
                atividade=atividade_instance,
                num_convenio=registro_dict['num_convenio'],
                parlamentar=registro_dict['parlamentar'],
                objeto=registro_dict['objeto'],
                oge_ogu = registro_dict['oge_ogu'].replace('R$', '').replace('.', '').replace(',', '.').strip(),
                cp_prefeitura = registro_dict['cp_prefeitura'].replace('R$', '').replace('.', '').replace(',', '.').strip(),
                valor_liberado = registro_dict['valor_liberado'].replace('R$', '').replace('.', '').replace(',', '.').strip(),
                prazo_vigencia=datetime.strptime(registro_dict['prazo_de_vigencia'], '%d-%m-%Y').date(),
                situacao=registro_dict['situacao'],
                providencia=registro_dict['providencia'],
                data_recepcao=datetime.strptime(registro_dict['data_recepcao'], '%d-%m-%Y').date(),
                data_inicio=None if registro_dict['data_inicio'] is None else datetime.strptime(registro_dict['data_inicio'], '%d-%m-%Y').date(),
                documento_pendente=registro_dict['documento_pendente'],
                documento_cancelado=registro_dict['documento_cancelado'],
                data_fim=None if registro_dict['data_fim'] is None else datetime.strptime(registro_dict['data_fim'], '%d-%m-%Y').date(),           
            )

            # Salve o novo registro na tabela original
            novo_registro.save()

            # Adicione o registro novamente à tabela original
            registros_anexados.append(registro_dict)

            # Remova o registro da lista de registros anexados
            registros_anexados = [r for r in registros_anexados if r['id'] != registro_id]

            # Atualize a lista de registros anexados e desanexados na sessão
            request.session['registros_anexados'] = registros_anexados

            # Adicione o registro à lista de registros desanexados
            registros_desanexados.append(registro_id)

            # Atualize a lista de registros desanexados na sessão
            request.session['registros_desanexados'] = registros_desanexados

    # Redirecione para a página que mostrará todos os registros desanexados
    return redirect('home')
    

def mostrar_registros_anexados(request):
    # Obtenha a lista de registros anexados e desanexados da sessão
    registros_anexados_ids = [registro['id'] for registro in request.session.get('registros_anexados', [])]
    registros_desanexados = request.session.get('registros_desanexados', [])

    # Recupere as instâncias dos registros anexados
    registros_anexados = RegistroFuncionarios.objects.filter(id__in=registros_anexados_ids)

    # Obtenha os registros anexados completos
    registros_anexados_completos = [
        registro for registro in request.session.get('registros_anexados', [])
        if registro['id'] in registros_anexados_ids
    ]
    
    # Obtenha os registros desanexados completos
    registros_desanexados_completos = RegistroFuncionarios.objects.filter(id__in=registros_desanexados)

    context = {
        'registros_anexados': registros_anexados_completos,
        'registros_desanexados': registros_desanexados_completos
    }

    return render(request, 'tabela_anexados.html', context)

def adicionar_registro_rf(request):
    if request.method == 'POST':
        nome = Nome.objects.get(id=request.POST.get('nome'))
        municipio = Municipio.objects.get(id=request.POST.get('municipio'))
        atividade = Atividade.objects.get(id=request.POST.get('atividade'))
        num_parcelamento = request.POST.get('num_parcelamento')
        objeto = request.POST.get('objeto')

        # Remova caracteres não numéricos da string e converta para float
        valor_total_str = request.POST.get('valor_total', '0').replace('R$', '').replace('.', '').replace(',', '.')
        valor_total = float(valor_total_str)

        prazo_vigencia = request.POST.get('prazo_vigencia')
        situacao = request.POST.get('situacao')
        providencia = request.POST.get('providencia')

        # Crie instâncias dos modelos relacionados...
        registro_rf = RegistroReceitaFederal(
            nome=nome,
            municipio=municipio,
            atividade=atividade,
            num_parcelamento=num_parcelamento,
            objeto=objeto,
            valor_total=valor_total,
            prazo_vigencia=prazo_vigencia,
            situacao=situacao,
            providencia=providencia,
        )

        # Salve o registro
        registro_rf.save()

        # Chame a função utilitária
        exibir_modal, dias_restantes = exibir_modal_prazo_vigencia(registro_rf)

        # Formate os valores 
        registro_rf.valor_total = f'R${valor_total:,.2f}'

        return redirect('inicio')
    
    # Recupere as opções para os campos estrangeiros...
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    atividades = Atividade.objects.all()
    registros_rf = RegistroReceitaFederal.objects.all()

    context = {
        'nomes': nomes,
        'municipios': municipios,
        'atividades': atividades,
        'messages': messages.get_messages(request),
        'registros_rf': registros_rf, 
    }

    return render(request, 'adicionar_registro_rf.html', context)

def visualizar_tabela_rf(request):
    # Recupere dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()
    atividades = Atividade.objects.all()

    # Recupere todos os registros
    registros_rf = RegistroReceitaFederal.objects.all()

    # Criar o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'atividades': atividades,
        'registros_rf': registros_rf,
    }

    # Renderize o modelo com o contexto
    return render(request, 'visualizar_tabela_rf.html', context)

def adicionar_registro_fgts_ind_con(request):
    if request.method == 'POST':
        try:
            competencia = request.POST.get('competencia')
            nome_empregado = request.POST.get('nome_empregado')
            pis = request.POST.get('pis')
            # Remova caracteres não numéricos da string
            pis = re.sub(r'\D', '', str(pis))
            admissao = request.POST.get('admissao')
            afastamento = request.POST.get('afastamento')
            cod_afastamento = request.POST.get('cod_afastamento')
            fgts = request.POST.get('fgts')
            gfip = request.POST.get('gfip')

            # Remova caracteres não numéricos da string e converta para float
            folha_de_pagamento_str = request.POST.get('folha_de_pagamento', '0').replace('R$', '').replace('.', '').replace(',', '.')
            folha_de_pagamento = float(folha_de_pagamento_str)

            arbitrado_str = request.POST.get('arbitrado', '0').replace('R$', '').replace('.', '').replace(',', '.')
            arbitrado = float(arbitrado_str)

            recomposto_str = request.POST.get('recomposto', '0').replace('R$', '').replace('.', '').replace(',', '.')
            recomposto = float(recomposto_str)

            rem_debito_str = request.POST.get('rem_debito', '0').replace('R$', '').replace('.', '').replace(',', '.')
            rem_debito = float(rem_debito_str)
            
            # Crie instâncias dos modelos relacionados...

            registro = RegistroFGTSIndCon(
                competencia=competencia,
                nome_empregado=nome_empregado,
                pis=pis,
                admissao=admissao,
                afastamento=afastamento,
                cod_afastamento=cod_afastamento,
                fgts=fgts,
                gfip=gfip,
                folha_de_pagamento=folha_de_pagamento,
                arbitrado=arbitrado,
                recomposto=recomposto,
                rem_debito=rem_debito,
            )

            registro.save()

            # Formate os valores
            registro.folha_de_pagamento = f'R${folha_de_pagamento:,.2f}'
            registro.arbitrado = f'R${arbitrado:,.2f}'
            registro.recomposto = f'R${recomposto:,.2f}'
            registro.rem_debito = f'R${rem_debito:,.2f}'

            return redirect('inicio')
        
        except (DataError, ValidationError) as e:
            # Se ocorrer um erro de dados (como um PIS inválido), você pode tratar aqui
            error_message = f"Erro ao salvar o registro: {str(e)}"
            return HttpResponse(error_message, status=400) 
    
    # Recuperar campos
    registros = RegistroFGTSIndCon.objects.all()

    context = {
        'messages': messages.get_messages(request),
        'registros': registros,
    }

    return render(request, 'adicionar_registro_fgts_ind_con.html', context)


def visualizar_tabela_fic(request):
    registros = RegistroFGTSIndCon.objects.all()

    context = {
        'registros': registros,
    }

    return render(request, 'visualizar_tabela_fic.html', context)


def adicionar_registro_administrativo(request):
    if request.method == 'POST':
        municipio = Municipio.objects.get(id=request.POST.get('municipio'))
        prazo_vigencia = request.POST.get('prazo_vigencia')
        num_contrato = request.POST.get('num_contrato')
        pub_femurn = request.POST.get('pub_femurn')
        na_cacex = 'na_cacex' in request.POST
        na_prefeitura = 'na_prefeitura' in request.POST

        registros = RegistroAdminstracao(
            municipio=municipio,
            prazo_vigencia=prazo_vigencia,
            num_contrato=num_contrato,
            pub_femurn=pub_femurn,
            na_cacex=na_cacex,
            na_prefeitura=na_prefeitura,
        )

        registros.save()

        return redirect('inicio') 
      
    
    municipios = Municipio.objects.all()
    registros = RegistroReceitaFederal.objects.all()

    context = {
        'messages': messages.get_messages(request),
        'municipios': municipios,
        'registros': registros,
    }

    return render(request, 'adicionar_registro_adminstrativo.html', context)

def visualizar_tabela_adminstrativa(request):
    registros = RegistroAdminstracao.objects.all()

    context = {
        'registros': registros,
    }

    return render(request, 'visualizar_tabela_adminstrativa.html', context)