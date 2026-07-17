from django import forms
from django.utils import timezone
from .models import Evento
from datetime import datetime


class EventoForm(forms.ModelForm):
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label='Data',
        input_formats=['%Y-%m-%d']
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        label='Hora',
        input_formats=['%H:%M']
    )

    data_limite_recorrencia = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label='Repetir até',
        input_formats=['%Y-%m-%d'],
        required=False
    )

    quantidade_repeticoes = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        label='Quantidade de Repetições',
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': '1'})
    )

    class Meta:
        model = Evento
        fields = ['titulo', 'data', 'hora', 'compartilhado', 'responsavel', 'categoria', 'cor', 'data_limite_recorrencia', 'quantidade_repeticoes']
        widgets = {
            'compartilhado': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Reunião de planejamento'
            }),
            'responsavel': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome do responsável'
            }),
            'cor': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-color'
            }),
        }
        labels = {
            'titulo': 'Título',
            'responsavel': 'Responsável',
            'cor': 'Cor',
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
        if data and hora:
            data_inicio = datetime.combine(data, hora)
            cleaned_data['data_inicio'] = timezone.make_aware(
                data_inicio,
                timezone.get_current_timezone(),
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.data_inicio = self.cleaned_data['data_inicio']
        if commit:
            instance.save()
        return instance
