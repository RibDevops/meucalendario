from django.db import models
from django.utils import timezone


class TipoEvento(models.TextChoices):
    REUNIAO = 'reuniao', 'Reunião'
    AUDITORIA = 'auditoria', 'Auditoria'
    CONSULTORIA = 'consultoria', 'Consultoria'
    TREINAMENTO = 'treinamento', 'Treinamento'
    OUTRO = 'outro', 'Outro'


class Evento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    tipo = models.CharField(
        max_length=20,
        choices=TipoEvento.choices,
        default=TipoEvento.REUNIAO,
        verbose_name='Tipo'
    )
    data_inicio = models.DateTimeField(verbose_name='Data e Hora de Início')
    data_fim = models.DateTimeField(verbose_name='Data e Hora de Término')
    local = models.CharField(max_length=200, blank=True, verbose_name='Local/Link')
    responsavel = models.CharField(max_length=100, blank=True, verbose_name='Responsável')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    duracao_minutos = models.PositiveIntegerField(default=30, verbose_name='Duração (minutos)')
    cor = models.CharField(
        max_length=7,
        default='#111827',
        verbose_name='Cor',
        help_text='Cor em hexadecimal (ex: #111827)'
    )
    notas = models.TextField(blank=True, verbose_name='Notas Internas')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['data_inicio']

    def __str__(self):
        return f"{self.titulo} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"

    @property
    def hora_inicio_formatada(self):
        return self.data_inicio.strftime('%H:%M')

    @property
    def hora_fim_formatada(self):
        return self.data_fim.strftime('%H:%M')

    @property
    def data_formatada(self):
        return self.data_inicio.strftime('%d/%m/%Y')

    @property
    def dia(self):
        return self.data_inicio.day

    @property
    def mes(self):
        return self.data_inicio.month

    @property
    def ano(self):
        return self.data_inicio.year


class ConfiguracaoAgenda(models.Model):
    titulo_agenda = models.CharField(max_length=200, default='Minha Agenda')
    subtitulo = models.CharField(max_length=300, blank=True)
    descricao = models.TextField(blank=True)
    tempo_padrao_evento = models.PositiveIntegerField(default=30, verbose_name='Tempo padrão (min)')
    intervalo_entre_eventos = models.PositiveIntegerField(default=0, verbose_name='Intervalo (min)')
    horario_inicio = models.TimeField(default='08:00', verbose_name='Horário inicial')
    horario_fim = models.TimeField(default='18:00', verbose_name='Horário final')
    dias_trabalho = models.CharField(
        max_length=20,
        default='1,2,3,4,5',
        verbose_name='Dias de trabalho',
        help_text='0=Dom, 1=Seg, ..., 6=Sáb. Separar por vírgula.'
    )
    timezone = models.CharField(max_length=50, default='America/Sao_Paulo')
    cor_primaria = models.CharField(max_length=7, default='#111827')
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Configuração da Agenda'
        verbose_name_plural = 'Configurações da Agenda'

    def __str__(self):
        return self.titulo_agenda
