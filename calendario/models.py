from django.db import models
from django.conf import settings
from django.utils import timezone


class Evento(models.Model):
    CATEGORIAS = [
        ('geral', 'Geral'),
        ('consulta', 'Consulta'),
        ('trabalho', 'Trabalho'),
        ('pessoal', 'Pessoal'),
        ('urgente', 'Urgente'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Título')
    criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos',
        null=True,
        blank=True,
        verbose_name='Criador',
    )
    compartilhado = models.BooleanField(default=True, verbose_name='Compartilhar')
    data_inicio = models.DateTimeField(verbose_name='Data e Hora')
    responsavel = models.CharField(max_length=100, blank=True, verbose_name='Responsável')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='geral', verbose_name='Categoria')
    cor = models.CharField(
        max_length=7,
        default='#6366f1',
        verbose_name='Cor',
        help_text='Cor em hexadecimal (ex: #6366f1)'
    )
    serie_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID da Série')
    data_limite_recorrencia = models.DateField(blank=True, null=True, verbose_name='Repetir até')
    google_event_id = models.CharField(max_length=255, blank=True, verbose_name='ID no Google Calendar')
    google_calendar_id = models.CharField(max_length=255, blank=True, verbose_name='Calendário Google')
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
