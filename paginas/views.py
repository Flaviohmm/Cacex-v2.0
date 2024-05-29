from plataforma.models import RegistroFuncionarios, Status, Nome, Setor, Municipio, Atividade
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa


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

    context = {
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


def gerador_pdf_tb_geral(request):
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
    # Dados para o gráfico de barras

    data = [contagem_registros]
    data_atividade = [contagem_atividades]

    # Criar o response PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grafico.pdf"'

    # Criar o objeto PDF
    pdf = canvas.Canvas(response, pagesize=letter)

    # Adicionar o gráfico de barras ao PDF
    chart = VerticalBarChart()
    chart.x = 0
    chart.y = 25
    chart.height = 250
    chart.width = 450
    chart.data = data
    chart.categoryAxis.categoryNames = orgaos_setor_labels

    drawing = Drawing(0, 0)
    drawing.add(chart)

    # Adicionar o desenho ao PDF
    drawing.drawOn(pdf, 50, 500)

    # Adicionar o gráfico de barras ao PDF
    chart_atividade = VerticalBarChart()
    chart_atividade.x = 0
    chart_atividade.y = 25
    chart_atividade.height = 250
    chart_atividade.width = 450
    chart_atividade.data = data_atividade
    chart_atividade.categoryAxis.categoryNames = atividades_labels

    drawing = Drawing(0, 0)
    drawing.add(chart_atividade)

    # Adicionar o desenho ao PDF
    drawing.drawOn(pdf, 50, 200)

    # Adicionar a contagem de registros concluidos em um retângulo
    rect_x = 50
    rect_y = 100
    rect_width = 150
    rect_heigth = 60

    pdf.rect(rect_x, rect_y, rect_width, rect_heigth, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(rect_x + 15, rect_y + 20, f"Total de Registros: {status_total}")

    # Adicionar a contagem de registros concluidos em um retângulo
    rect_x = 211
    rect_y = 100
    rect_width = 100
    rect_heigth = 50

    pdf.rect(rect_x, rect_y, rect_width, rect_heigth, fill=1)
    pdf.setFillColor(colors.green)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(rect_x + 15, rect_y + 20, f"Concluídos: {registros_concluidos}")

    # Adicionar a contagem de registros concluidos em um retângulo
    rect_x = 320
    rect_y = 100
    rect_width = 100
    rect_heigth = 50

    pdf.rect(rect_x, rect_y, rect_width, rect_heigth, fill=1)
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(rect_x + 15, rect_y + 20, f"Pendentes: {registros_pendentes}")

    # Adicionar a contagem de registros concluidos em um retângulo
    rect_x = 425
    rect_y = 100
    rect_width = 110
    rect_heigth = 50

    pdf.rect(rect_x, rect_y, rect_width, rect_heigth, fill=1)
    pdf.setFillColor(colors.aquamarine)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(rect_x + 15, rect_y + 20, f"Não Iniciados: {registros_nao_iniciados}")

    # Adicionar a contagem de registros concluidos em um retângulo
    rect_x = 50
    rect_y = 47
    rect_width = 110
    rect_heigth = 50

    pdf.rect(rect_x, rect_y, rect_width, rect_heigth, fill=1)
    pdf.setFillColor(colors.red)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(rect_x + 15, rect_y + 20, f"Em Análise: {registros_em_analises}")

    # Adicionar a contagem de registros concluidos em um retângulo
    rect_x = 170
    rect_y = 47
    rect_width = 110
    rect_heigth = 50

    pdf.rect(rect_x, rect_y, rect_width, rect_heigth, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(rect_x + 15, rect_y + 20, f"Suspensos: {registros_suspensos}")

    # Fechar o PDF
    pdf.showPage()
    pdf.save()

    return response


def gerar_pdf(request):
    registros = RegistroFuncionarios.objects.all()

    template_path = 'tabela_geral_pdf.html'
    context = {
        'registros': registros
    }
    print(registros)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_geral.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response

def gerar_pdf_caixa_municipios_selecionados(request):
    orgao_setor_caixa = Setor.objects.get(orgao_setor='CAIXA')

    municipio_id = request.GET.get('municipio')

    registros_filtrados = RegistroFuncionarios.objects.filter(orgao_setor=orgao_setor_caixa)

    if municipio_id:
        registros_filtrados = registros_filtrados.filter(municipio__id=municipio_id)

    template_path = 'tabela_geral_pdf.html'
    context = {
        'registros': registros_filtrados
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_CAIXA.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response

def gerar_pdf_tabela_estado(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='ESTADO')

    # Recuperar dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()

    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    template_path = 'tabela_geral_pdf.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_ESTADO.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response

def gerar_pdf_tabela_fnde(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='FNDE')

    # Recuperar dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()

    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    template_path = 'tabela_geral_pdf.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_FNDE.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response

def gerar_pdf_tabela_simec(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='SIMEC')

    # Recuperar dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()

    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    template_path = 'tabela_geral_pdf.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_SIMEC.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response

def gerar_pdf_tabela_fns(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='FNS')

    # Recuperar dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()

    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    template_path = 'tabela_geral_pdf.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_FNS.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response

def gerar_pdf_tabela_entidade(request):
    registros = RegistroFuncionarios.objects.filter(orgao_setor__orgao_setor='Entidade')

    # Recuperar dados para as listas suspensas
    nomes = Nome.objects.all()
    municipios = Municipio.objects.all()

    # Crie o contexto com os dados
    context = {
        'nomes': nomes,
        'municipios': municipios,
        'registros': registros,
    }

    template_path = 'tabela_geral_pdf.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tabela_Entidade.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)
    
    return response