import calendar
import json
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Evento
from .forms import EventoForm


def calendario_view(request):
    hoje = timezone.now().date()

    try:
        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))
    except (ValueError, TypeError):
        ano = hoje.year
        mes = hoje.month

    try:
        dia = int(request.GET.get('dia', hoje.day))
    except (ValueError, TypeError):
        dia = hoje.day

    try:
        data_selecionada = date(ano, mes, dia)
    except ValueError:
        dia = min(dia, calendar.monthrange(ano, mes)[1])
        data_selecionada = date(ano, mes, dia)

    cal = calendar.Calendar(firstweekday=6)
    dias_mes = cal.monthdayscalendar(ano, mes)

    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    nome_mes = meses_pt[mes]

    dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

    dias_semana_abrev_full = ['Dom.', 'Seg.', 'Ter.', 'Qua.', 'Qui.', 'Sex.', 'Sáb.']
    iso_wd = data_selecionada.isoweekday()
    idx_semana = iso_wd % 7
    dias_semana_abrev = dias_semana_abrev_full[idx_semana]

    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
    eventos_mes = Evento.objects.filter(
        data_inicio__date__gte=primeiro_dia,
        data_inicio__date__lte=ultimo_dia
    ).order_by('data_inicio')

    eventos_por_dia = {}
    for evento in eventos_mes:
        d = evento.data_inicio.day
        if d not in eventos_por_dia:
            eventos_por_dia[d] = []
        eventos_por_dia[d].append(evento)

    eventos_dia = Evento.objects.filter(
        data_inicio__date=data_selecionada
    ).order_by('data_inicio')

    mes_anterior = mes - 1 if mes > 1 else 12
    ano_anterior = ano if mes > 1 else ano - 1
    mes_posterior = mes + 1 if mes < 12 else 1
    ano_posterior = ano if mes < 12 else ano + 1

    context = {
        'ano': ano,
        'mes': mes,
        'nome_mes': nome_mes,
        'dia': data_selecionada.day,
        'data_selecionada': data_selecionada,
        'dias_semana': dias_semana,
        'dias_semana_abrev': dias_semana_abrev,
        'dias_mes': dias_mes,
        'eventos_por_dia': eventos_por_dia,
        'eventos_dia': eventos_dia,
        'hoje': hoje,
        'mes_anterior': mes_anterior,
        'ano_anterior': ano_anterior,
        'mes_posterior': mes_posterior,
        'ano_posterior': ano_posterior,
    }

    return render(request, 'calendario/calendario.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def evento_criar(request):
    try:
        if request.content_type == 'application/json':
            dados = json.loads(request.body)
            form = EventoForm(dados)
        else:
            form = EventoForm(request.POST)

        if form.is_valid():
            evento = form.save()
            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Evento criado com sucesso!',
                'evento': _serializar(evento)
            })
        else:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Erro de validação',
                'erros': {k: v[0] for k, v in form.errors.items()}
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'sucesso': False, 'mensagem': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def evento_editar(request, pk):
    try:
        evento = get_object_or_404(Evento, pk=pk)

        if request.content_type == 'application/json':
            dados = json.loads(request.body)
            form = EventoForm(dados, instance=evento)
        else:
            form = EventoForm(request.POST, instance=evento)

        if form.is_valid():
            evento = form.save()
            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Evento atualizado com sucesso!',
                'evento': _serializar(evento)
            })
        else:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Erro de validação',
                'erros': {k: v[0] for k, v in form.errors.items()}
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'sucesso': False, 'mensagem': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def evento_excluir(request, pk):
    try:
        evento = get_object_or_404(Evento, pk=pk)
        titulo = evento.titulo
        evento.delete()
        return JsonResponse({'sucesso': True, 'mensagem': f'Evento "{titulo}" excluído!'})
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)}, status=500)


def evento_detalhes(request, pk):
    try:
        evento = get_object_or_404(Evento, pk=pk)
        return JsonResponse({'sucesso': True, 'evento': _serializar(evento)})
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)}, status=500)


def _serializar(evento):
    return {
        'id': evento.id,
        'titulo': evento.titulo,
        'data': evento.data_inicio.strftime('%Y-%m-%d'),
        'hora': evento.data_inicio.strftime('%H:%M'),
        'responsavel': evento.responsavel,
        'cor': evento.cor,
    }
