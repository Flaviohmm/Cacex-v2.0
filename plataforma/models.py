from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
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


class Status(models.TextChoices):
    NAO_INICIADO = 'Não Iniciado', 'Não Iniciado'
    EM_ANALISE = 'Em Análise', 'Em Análise'
    PENDENTE = 'Pendente', 'Pendente'
    SUSPENSO = 'Suspenso', 'Suspenso'
    CONCLUIDO = 'Concluído', 'Concluído'


class RegistroFuncionarios(models.Model):
    class Meta:
        verbose_name_plural = "Registros de Funcionários"

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
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NAO_INICIADO)
    data_recepcao = models.DateField()
    data_inicio = models.DateField(null=True, blank=True)
    documento_pendente = models.BooleanField(default=False)
    documento_cancelado = models.BooleanField(default=False)
    data_fim = models.DateField(null=True, blank=True)
    duracao_dias_uteis = models.IntegerField(default=0)

    def calcular_valores(self):
        # Converter os valores para decimais
        valor_total = Decimal(str(self.oge_ogu)) + Decimal(str(self.cp_prefeitura))
        falta_liberar = valor_total - Decimal(str(self.valor_liberado))

        # Calcular o Valor Total e Falta Liberar
        return valor_total, falta_liberar
        

    def exibir_modal_prazo_vigencia(self):
        hoje = timezone.now().date()
        prazo_vigencia = self.prazo_vigencia
        dias_restantes = (prazo_vigencia - hoje).days
        return dias_restantes <= 30, dias_restantes

    def dia_trabalho_total(self):
        if not self.data_inicio or not self.data_fim:
            return 0

        # Converta para objetos date, se necessário
        if isinstance(self.data_inicio, str):
            self.data_inicio = datetime.strptime(self.data_inicio, "%Y-%m-%d").date()
        if isinstance(self.data_fim, str):
            self.data_fim = datetime.strptime(self.data_fim, "%Y-%m-%d").date()

        delta = self.data_fim - self.data_inicio
        dias_uteis = sum(1 for i in range(delta.days + 1) if (self.data_inicio + timedelta(days=i)).weekday() < 5)

        return dias_uteis
    
    def save(self, *args, **kwargs):
        if not self.prazo_vigencia or not self.data_recepcao:
            raise ValueError("A data de prazo de vigência e data de recepção são obrigatórias.")

        if self.prazo_vigencia and self.prazo_vigencia.strip():  # Verifica se a string não está vazia após remoção de espaços
            try:
                # Converta a string para objeto date
                self.prazo_vigencia = datetime.strptime(self.prazo_vigencia, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Formato de data inválido para prazo de vigência. Deve ser no formato YYYY-MM-DD.")
        
        # Chame a função calcular_valores e obtenha os valores calculados
        valor_total, falta_liberar = self.calcular_valores()

        # Use os valores calculados conforme necessário
        self.valor_total = valor_total
        self.falta_liberar = falta_liberar

        # Verifica se as datas não estão vazias antes de salvar
        if not self.data_inicio:
            self.data_inicio = None
        if not self.data_fim:
            self.data_fim = None

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
        # Use os valores calculados ao exibir o objeto como uma string
        valor_total, falta_liberar = self.calcular_valores()
        return (
            f"{self.nome.nome} | {self.orgao_setor.orgao_setor} | {self.municipio.municipio} | "
            f"{self.atividade.atividade} | {self.num_convenio} | {self.parlamentar} | {self.objeto} | "
            f"{self.oge_ogu} | {self.cp_prefeitura} | {valor_total} | {self.valor_liberado} | "
            f"{falta_liberar} | {self.prazo_vigencia} | {self.situacao} | {self.providencia} | "
            f"{self.status} | {self.data_recepcao} | {self.data_inicio} | {self.documento_pendente} | "
            f"{self.documento_cancelado} | {self.data_fim} | {self.duracao_dias_uteis}"
        )