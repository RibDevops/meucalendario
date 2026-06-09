from django.db import models
from django.utils import timezone


class Evento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título')
    data_inicio = models.DateTimeField(verbose_name='Data e Hora')
    responsavel = models.CharField(max_length=100, blank=True, verbose_name='Responsável')
    cor = models.CharField(
        max_length=7,
        default='#6366f1',
        verbose_name='Cor',
        help_text='Cor em hexadecimal (ex: #6366f1)'
    )
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
