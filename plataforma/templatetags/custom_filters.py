from django import template
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
