from django.contrib import admin
from .models import Evento, ConfiguracaoAgenda


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'data_inicio', 'data_fim', 'responsavel', 'local']
    list_filter = ['tipo', 'data_inicio']
    search_fields = ['titulo', 'descricao', 'responsavel', 'local']
    date_hierarchy = 'data_inicio'
    ordering = ['-data_inicio']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'tipo', 'cor')
        }),
        ('Data e Hora', {
            'fields': ('data_inicio', 'data_fim', 'duracao_minutos')
        }),
        ('Contato e Local', {
            'fields': ('local', 'responsavel', 'email', 'telefone')
        }),
        ('Outros', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConfiguracaoAgenda)
class ConfiguracaoAgendaAdmin(admin.ModelAdmin):
    list_display = ['titulo_agenda', 'ativo']
