from django import forms
from django.core.exceptions import ValidationError
from .models import Evento, TipoEvento
from datetime import datetime, timedelta


class EventoForm(forms.ModelForm):
    data = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-input'
            }
        ),
        label='Data',
        input_formats=['%Y-%m-%d']
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'form-input'
            }
        ),
        label='Hora de Início',
        input_formats=['%H:%M']
    )

    class Meta:
        model = Evento
        fields = [
            'titulo', 'descricao', 'tipo', 'data', 'hora',
            'duracao_minutos', 'local', 'responsavel',
            'email', 'telefone', 'cor', 'notas'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Auditoria de IA para Empresas'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Descrição do evento...'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'duracao_minutos': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 5,
                'step': 5,
                'value': 30
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Google Meet ou Sala 101'
            }),
            'responsavel': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome do responsável'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '(00) 00000-0000'
            }),
            'cor': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-color'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Notas internas...'
            }),
        }
        labels = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'tipo': 'Tipo de Evento',
            'duracao_minutos': 'Duração (minutos)',
            'local': 'Local ou Link',
            'responsavel': 'Responsável',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'cor': 'Cor',
            'notas': 'Notas Internas',
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance:
            self.fields['data'].initial = instance.data_inicio.date()
            self.fields['hora'].initial = instance.data_inicio.time()

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora = cleaned_data.get('hora')
        duracao = cleaned_data.get('duracao_minutos', 30)

        if data and hora:
            data_inicio = datetime.combine(data, hora)
            cleaned_data['data_inicio'] = data_inicio
            cleaned_data['data_fim'] = data_inicio + timedelta(minutes=duracao)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.data_inicio = self.cleaned_data['data_inicio']
        instance.data_fim = self.cleaned_data['data_fim']
        if commit:
            instance.save()
        return instance


class EventoQuickForm(forms.ModelForm):
    """Formulário rápido para criar evento em um clique"""
    data = forms.DateField(widget=forms.HiddenInput())
    hora = forms.TimeField(widget=forms.HiddenInput())

    class Meta:
        model = Evento
        fields = ['titulo', 'data', 'hora', 'duracao_minutos', 'tipo', 'local']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Título do evento'
            }),
            'duracao_minutos': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 5,
                'step': 5,
                'value': 30
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'local': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Local/Link'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora = cleaned_data.get('hora')
        duracao = cleaned_data.get('duracao_minutos', 30)

        if data and hora:
            data_inicio = datetime.combine(data, hora)
            cleaned_data['data_inicio'] = data_inicio
            cleaned_data['data_fim'] = data_inicio + timedelta(minutes=duracao)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.data_inicio = self.cleaned_data['data_inicio']
        instance.data_fim = self.cleaned_data['data_fim']
        if commit:
            instance.save()
        return instance
