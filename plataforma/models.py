from django.db import models
from django.utils import timezone
import numpy as np


class Nome(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome
    
class Setor(models.Model):
    orgao_setor = models.CharField(max_length=255)

    def __str__(self):
        return self.orgao_setor
    
class Municipio(models.Model):
    municipio = models.CharField(max_length=255)

    def __str__(self):
        return self.municipio

class Atividade(models.Model):
    atividade = models.CharField(max_length=255)

    def __str__(self):
        return self.atividade

class Status(models.Model):
    NAO_INICIADO = 'nao_iniciado', 'Não Iniciado'
    EM_ANALISE = 'em_analise', 'Em Análise'
    PENDENTE = 'pendente', 'Pendente'
    SUSPENSO = 'suspenso', 'Suspenso'
    CONCLUIDO = 'concluido', 'Concluído'

class RegistroFuncionarios(models.Model):
    nome = models.ForeignKey(Nome, on_delete=models.CASCADE)
    orgao_setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    num_convenio = models.CharField(max_length=255)
    parlamentar = models.CharField(max_length=255)
    objeto = models.CharField(max_length=255)
    oge_ogu = models.DecimalField(max_digits=10, decimal_places=2)
    cp_prefeitura = models.DecimalField(max_digits=10, decimal_places=2)
    valor_liberado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prazo_vigencia = models.DateField()
    situacao = models.CharField(max_length=255)
    providencia = models.CharField(max_length=255)
    data_recepcao = models.DateField()
    data_inicio = models.DateField(null=True, blank=True)
    documento_pendente = models.BooleanField(default=False)
    documento_cancelado = models.BooleanField(default=False)
    data_fim = models.DateField(null=True, blank=True)
    duracao_dias_uteis = models.IntegerField(default=0)

    def calcular_valores(self):
        # Calcular o Valor Total
        self.valor_total = self.oge_ogu + self.cp_prefeitura

        # Calcular o Falta Liberar
        self.falta_liberar = self.valor_total - self.valor_liberado

    def exibir_modal_prazo_vigencia(self):
        hoje = timezone.now().date()
        prazo_vigencia = self.prazo_vigencia
        dias_restantes = (prazo_vigencia - hoje).days
        return dias_restantes <= 30, dias_restantes

    def dia_trabalho_total(self):
        if self.data_inicio and self.data_fim:
            feriado_facultativo = [] # Substitua isso pela lista de feriados facultativos
            dias_uteis = np.busday_count(self.data_inicio, self.data_fim, holidays=feriado_facultativo)
            return dias_uteis
        return 0
    
    def save(self, *args, **kwargs):
        self.calcular_valores()

        if not self.data_inicio:
            self.status = Status.NAO_INICIADO
        elif self.documento_pendente:
            self.status = Status.PENDENTE
        elif self.documento_cancelado:
            self.status = Status.SUSPENSO
        elif self.data_fim:
            self.status = Status.CONCLUIDO
        else:
            self.status = Status.EM_ANALISE

        self.duracao_dias_uteis = self.dia_trabalho_total()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome + " | " + self.orgao_setor + " | " + self.municipio + " | " + self.atividade + " | " + self.num_convenio + " | " + self.parlamentar + " | " + self.objeto + " | " + self.oge_ogu + " | " + self.cp_prefeitura + " | " + self.valor_total + " | " + self.valor_liberado + " | " + self.falta_liberar
