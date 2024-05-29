from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from autenticar.models import CustomUser
from .templatetags.custom_filters import format_currency
import numpy as np
import json


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
        verbose_name_plural = "Registros da Tabela Geral"

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
        falta_liberar = Decimal(str(self.oge_ogu)) - Decimal(str(self.valor_liberado))

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

        if self.prazo_vigencia and isinstance(self.prazo_vigencia, str) and self.prazo_vigencia.strip():  # Verifica se a string não está vazia após remoção de espaços
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

class DecimalJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif callable(obj):
            # Se obj for uma função/método, converta para uma string representativa
            return f"{obj.__module__}.{obj.__name__}"
        return super().default(obj)

class Historico(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    acao = models.CharField(max_length=255)
    data = models.DateTimeField(auto_now_add=True)
    dados_anteriores = models.JSONField(default=dict, encoder=DecimalJSONEncoder)
    registro = models.ForeignKey(RegistroFuncionarios, on_delete=models.CASCADE)
    dados_atuais = models.JSONField(default=dict, encoder=DecimalJSONEncoder)
    dados_alterados = models.JSONField(default=dict, encoder=DecimalJSONEncoder)

    def save(self, *args, **kwargs):
        if self.pk is not None: # Verifica se o objeto já existe no banco (edição)
            # Obtém o objeto existente no banco para capturar os dados atuais
            objeto_existente = Historico.objects.get(pk=self.pk)

            # Atualiza os dados anteriores com base nos dados atuais do objeto existente
            self.dados_anteriores = objeto_existente.dados_atuais

            # Atualiza os dados atuais com os dados atuais do objeto atual
            self.dados_atuais = self.get_current_data()

            # Calcula os dados alterados
            self.dados_alterados = self.comparar_valores(self.dados_anteriores, self.dados_atuais)
        else: # Novo objeto
            self.dados_atuais = self.get_current_data()

        super(Historico, self).save(*args, **kwargs)

    def get_dados_anteriores_log(self, logs):
        dados_anteriores = {}

        for log in logs:
            if 'Dados Anteriores' in log:
                parsed_data = log[log.find('{'):log.rfind('}')+1]
                dados_anteriores = eval(parsed_data)

        return dados_anteriores

    def get_current_data(self):
        # Acessando os dados atuais do modelo RegistroFuncionarios associado
        dados_atuais = {
            'nome': self.registro.nome.nome,
            'orgao_setor': self.registro.orgao_setor.orgao_setor,
            'municipio': self.registro.municipio.municipio,
            'atividade': self.registro.atividade.atividade,
            'num_convenio': self.registro.num_convenio,
            'parlamentar': self.registro.parlamentar,
            'objeto': self.registro.objeto,
            'oge_ogu': format_currency(self.registro.oge_ogu),
            'cp_prefeitura': format_currency(self.registro.cp_prefeitura),
            'valor_total': format_currency(self.registro.valor_total),
            'valor_liberado': format_currency(self.registro.valor_liberado),
            'falta_liberar': format_currency(self.registro.falta_liberar),
            'prazo_vigencia': self.registro.prazo_vigencia.strftime("%d/%m/%Y"),
            'situacao': self.registro.situacao,
            'providencia': self.registro.providencia,
            'status': self.registro.status,
            'data_recepcao': self.registro.data_recepcao.strftime("%d/%m/%Y"),
            'data_inicio': self.registro.data_inicio.strftime("%d/%m/%Y") if self.registro.data_inicio else "",
            'documento_pendente': 'Sim' if self.registro.documento_pendente else 'Não',
            'documento_cancelado': 'Sim' if self.registro.documento_cancelado else 'Não',
            'data_fim': self.registro.data_fim.strftime("%d/%m/%Y") if self.registro.data_fim else "",
            'duracao_dias_uteis': self.registro.duracao_dias_uteis
        }

        return dados_atuais
    
    def comparar_valores(self, dados_anteriores, dados_atuais):
        diff = []
        for key, value_anterior in dados_anteriores.items():
            if key in dados_atuais:
                value_atual = dados_atuais[key]
                if value_atual != value_anterior:
                    diff.append((key, value_anterior, value_atual))
        return diff

    def __str__(self):
        return f'{self.usuario} - {self.acao} em {self.data} | \n Dados Anteriores: {self.dados_anteriores} ->  \n Dados Atuais: {self.dados_atuais}' 
    
class RegistroReceitaFederal(models.Model):
    class Meta:
        verbose_name_plural = "Tabela da Receita Federal"

    nome = models.ForeignKey(Nome, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    num_parcelamento = models.IntegerField()
    objeto = models.CharField(max_length=255)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    prazo_vigencia = models.DateField()
    situacao = models.CharField(max_length=255)
    providencia = models.CharField(max_length=255)

    def exibir_modal_prazo_vigencia(self):
        hoje = timezone.now().date()
        prazo_vigencia = self.prazo_vigencia
        dias_restantes = (prazo_vigencia - hoje).days
        return dias_restantes <= 30, dias_restantes

    def save(self, *args, **kwargs):
        if not self.prazo_vigencia:
            raise ValueError("A data do prazo de vigência é obrigatório")
        
        if self.prazo_vigencia and isinstance(self.prazo_vigencia, str) and self.prazo_vigencia.strip():  # Verifica se a string não está vazia após remoção de espaços
            try:
                # Converta a string para objeto date
                self.prazo_vigencia = datetime.strptime(self.prazo_vigencia, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Formato de data inválido para prazo de vigência. Deve ser no formato YYYY-MM-DD.")
            
        super().save(*args, **kwargs)
            
    def __str__(self):
        return (
            f"{self.nome.nome} | {self.municipio.municipio} | {self.atividade.atividade} | {self.num_parcelamento} | "
            f"{self.objeto} | {self.valor_total} | {self.prazo_vigencia} | {self.situacao} |"
            f"{self.providencia}"
        )
    

class RegistroFGTSIndCon(models.Model):
    class Meta:
        verbose_name_plural = "Tabela de FGTS, Individualização e Contabilidade"

    competencia = models.CharField(max_length=255)
    nome_empregado = models.CharField(max_length=255)
    pis = models.BigIntegerField(
        validators=[
            MaxValueValidator(99999999999),  # Valor máximo de 11 dígitos
            MinValueValidator(10000000000)   # Valor mínimo de 11 dígitos
        ]
    )
    admissao = models.DateField()
    afastamento = models.DateField()
    cod_afastamento = models.IntegerField()
    fgts = models.IntegerField()
    gfip = models.IntegerField()
    folha_de_pagamento = models.DecimalField(max_digits=10, decimal_places=2)
    arbitrado = models.DecimalField(max_digits=10, decimal_places=2)
    recomposto = models.DecimalField(max_digits=10, decimal_places=2)
    rem_debito = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.competencia} | {self.nome_empregado} | {self.pis} | {self.admissao} | {self.afastamento} | "
            f"{self.cod_afastamento} | {self.fgts} | {self.gfip} | {self.folha_de_pagamento} | "
            f"{self.arbitrado} | {self.recomposto} | {self.rem_debito} "
        )
    

class RegistroAdminstracao(models.Model):
    class Meta:
        verbose_name_plural = "Tabela Adminstrativa" 

    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)  
    prazo_vigencia = models.DateField()
    num_contrato = models.CharField(max_length=255)
    pub_femurn = models.CharField(max_length=255)
    na_cacex = models.BooleanField(default=False)
    na_prefeitura = models.BooleanField(default=False)  

    def exibir_modal_prazo_vigencia(self):
        hoje = timezone.now().date()
        prazo_vigencia = self.prazo_vigencia
        dias_restantes = (prazo_vigencia - hoje).days
        return dias_restantes <= 30, dias_restantes

    def save(self, *args, **kwargs):
        if not self.prazo_vigencia:
            raise ValueError("A data do prazo de vigência é obrigatório")
        
        if self.prazo_vigencia and isinstance(self.prazo_vigencia, str) and self.prazo_vigencia.strip():  # Verifica se a string não está vazia após remoção de espaços
            try:
                # Converta a string para objeto date
                self.prazo_vigencia = datetime.strptime(self.prazo_vigencia, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Formato de data inválido para prazo de vigência. Deve ser no formato YYYY-MM-DD.")
            
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.municipio.municipio} | {self.prazo_vigencia} | {self.num_contrato} | " 
            f"{self.pub_femurn} | {self.na_cacex} | {self.na_prefeitura}"
        )  
