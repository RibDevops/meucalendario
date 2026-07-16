from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data_inicio', 'criador', 'compartilhado', 'responsavel', 'cor']
    list_filter = ['compartilhado', 'data_inicio']
    search_fields = ['titulo', 'responsavel']
    date_hierarchy = 'data_inicio'
    ordering = ['-data_inicio']
