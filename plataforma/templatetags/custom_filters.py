from django import template
from datetime import datetime, date
import locale
import re

register = template.Library()

@register.filter(name='format_currency')
def format_currency(value):
    try: 
        # Tente converter o valor para float
        numeric_value = float(value)

        # Formate o valor como uma string com duas casas decimais e ponto como separador de milhar
        formatted_value = '{:,.2f}'.format(numeric_value)

        # Adicione o simbolo da moeda brasileira R$
        formatted_value = 'R$ ' + formatted_value.replace(',', 'v').replace('.', ',').replace('v', '.')

        return formatted_value
    except ValueError:
        # Trate o caso em que a conversão para float falha
        return value
    

@register.filter(name='formatar_data')
def formatar_data(value):
    if isinstance(value, date):
        # Se value já for um objeto de data, usar diretamente o strftime
        return value.strftime('%d/%m/%Y')
    else:
        # Se value for uma string, converter para objeto de data e depois formatar
        data_obj = datetime.strptime(value, '%d de %B de %Y')
        return data_obj.strftime('%d/%m/%Y')
    

@register.filter(name='formatar_pis')
def formatar_pis(pis):

    pis_str = str(pis)

    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', pis_str)

    # Adiciona a máscara
    formatted_pis = re.sub(r'(\d{3})(\d{5})(\d{2})(\d{1})$', r'\1.\2.\3-\4', numeros)

    return formatted_pis
