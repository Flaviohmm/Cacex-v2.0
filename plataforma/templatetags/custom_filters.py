from django import template
from datetime import datetime, date
import locale

register = template.Library()

@register.filter(name='format_currency')
def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    try: 
        #Converta o valor para um número antes de chamar locale.currency
        numeric_value = float(value)
        return locale.currency(numeric_value, grouping=True)
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
