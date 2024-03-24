from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np


def calcular_valores(registro):
    # Converter os valores para decimais
    valor_total = Decimal(str(registro.oge_ogu)) + Decimal(str(registro.cp_prefeitura))
    falta_liberar = Decimal(str(registro.oge_ogu)) - Decimal(str(registro.valor_liberado))

    # Calcular o Valor Total e Falta Liberar
    return valor_total, falta_liberar


def exibir_modal_prazo_vigencia(registro):
    hoje = timezone.now().date()
    try:
        dias_restantes = (registro.prazo_vigencia - hoje).days
        return dias_restantes <= 30, dias_restantes
    except Exception as e:
        # Log da exceção ou outro tratamento apropriado
        return False, 0


def dia_trabalho_total(data_inicio, data_fim):
    if not data_inicio or not data_fim:
        return 0

    # Converta para objetos date, se necessário
    if isinstance(data_inicio, str):
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
    if isinstance(data_fim, str):
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

    delta = data_fim - data_inicio
    dias_uteis = sum(1 for i in range(delta.days + 1) if (data_inicio + timedelta(days=i)).weekday() < 5)

    return dias_uteis
