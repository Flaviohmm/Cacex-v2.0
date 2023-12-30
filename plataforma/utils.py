from django.utils import timezone
import numpy as np


def calcular_valores(registro):
    registro.valor_total = registro.oge_ogu + registro.cp_prefeitura
    registro.falta_liberar = registro.valor_total - registro.valor_liberado

def exibir_modal_prazo_vigencia(registro):
    hoje = timezone.now().date()
    dias_restantes = (registro.prazo_vigencia - hoje).days
    return dias_restantes <= 30, dias_restantes

def dia_trabalho_total(data_inicio, data_fim, feriado_facultativo=[]):
    if data_inicio and data_fim:
        dias_uteis = np.busday_count(data_inicio, data_fim, holidays=feriado_facultativo)
        return dias_uteis
    return 0
