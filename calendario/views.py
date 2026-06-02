import calendar
import json
from datetime import datetime, timedelta, date

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Evento
from .forms import EventoForm, EventoQuickForm


def calendario_view(request):
    """View principal do calendário"""
    hoje = timezone.now().date()

    # Pegar mês e ano da URL ou usar o atual
    try:
        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))
    except (ValueError, TypeError):
        ano = hoje.year
        mes = hoje.month

    # Pegar dia selecionado
    try:
        dia = int(request.GET.get('dia', hoje.day))
    except (ValueError, TypeError):
        dia = hoje.day

    # Validar data
    try:
        data_selecionada = date(ano, mes, dia)
    except ValueError:
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dia = min(dia, ultimo_dia)
        data_selecionada = date(ano, mes, dia)

    # Normalizar data selecionada
    if data_selecionada < date(ano, mes, 1):
        data_selecionada = date(ano, mes, 1)
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    if data_selecionada.day > ultimo_dia_mes:
        data_selecionada = date(ano, mes, ultimo_dia_mes)

    # Calendário mensal
    cal = calendar.Calendar(firstweekday=6)  # Domingo como primeiro dia
    dias_mes = cal.monthdayscalendar(ano, mes)

    # Nome do mês em português
    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    nome_mes = meses_pt[mes]

    # Dias da semana
    dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

    # Eventos do mês
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
    eventos_mes = Evento.objects.filter(
        data_inicio__date__gte=primeiro_dia,
        data_inicio__date__lte=ultimo_dia
    ).order_by('data_inicio')

    # Agrupar eventos por dia
    eventos_por_dia = {}
    for evento in eventos_mes:
        dia_evento = evento.data_inicio.day
        if dia_evento not in eventos_por_dia:
            eventos_por_dia[dia_evento] = []
        eventos_por_dia[dia_evento].append(evento)

    # Horários disponíveis do dia selecionado (8h às 22h, de 30 em 30 min)
    horarios = []
    for h in range(8, 22):
        for m in [0, 30]:
            hora = f"{h:02d}:{m:02d}"
            # Verificar se já existe evento neste horário
            hora_dt = datetime.strptime(hora, '%H:%M').time()
            ocupado = eventos_mes.filter(
                data_inicio__date=data_selecionada,
                data_inicio__time__lte=hora_dt,
                data_fim__time__gt=hora_dt
            ).exists()
            horarios.append({
                'hora': hora,
                'ocupado': ocupado
            })

    # Eventos do dia selecionado
    eventos_dia = Evento.objects.filter(
        data_inicio__date=data_selecionada
    ).order_by('data_inicio')

    # Navegação
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
        'dias_mes': dias_mes,
        'eventos_por_dia': eventos_por_dia,
        'horarios': horarios,
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
    """Criar evento via AJAX"""
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
                'evento': {
                    'id': evento.id,
                    'titulo': evento.titulo,
                    'tipo': evento.tipo,
                    'data': evento.data_formatada,
                    'hora_inicio': evento.hora_inicio_formatada,
                    'hora_fim': evento.hora_fim_formatada,
                    'local': evento.local,
                    'responsavel': evento.responsavel,
                    'cor': evento.cor,
                }
            })
        else:
            erros = {campo: erro[0] for campo, erro in form.errors.items()}
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Erro de validação',
                'erros': erros
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'sucesso': False,
            'mensagem': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'mensagem': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def evento_editar(request, pk):
    """Editar evento via AJAX"""
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
                'evento': {
                    'id': evento.id,
                    'titulo': evento.titulo,
                    'tipo': evento.tipo,
                    'data': evento.data_formatada,
                    'hora_inicio': evento.hora_inicio_formatada,
                    'hora_fim': evento.hora_fim_formatada,
                    'local': evento.local,
                    'responsavel': evento.responsavel,
                    'cor': evento.cor,
                }
            })
        else:
            erros = {campo: erro[0] for campo, erro in form.errors.items()}
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Erro de validação',
                'erros': erros
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'sucesso': False,
            'mensagem': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'mensagem': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def evento_excluir(request, pk):
    """Excluir evento via AJAX"""
    try:
        evento = get_object_or_404(Evento, pk=pk)
        titulo = evento.titulo
        evento.delete()
        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Evento "{titulo}" excluído com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'mensagem': str(e)
        }, status=500)


def evento_detalhes(request, pk):
    """Obter detalhes do evento via AJAX (GET)"""
    try:
        evento = get_object_or_404(Evento, pk=pk)
        return JsonResponse({
            'sucesso': True,
            'evento': {
                'id': evento.id,
                'titulo': evento.titulo,
                'descricao': evento.descricao,
                'tipo': evento.tipo,
                'tipo_display': evento.get_tipo_display(),
                'data': evento.data_inicio.strftime('%Y-%m-%d'),
                'hora': evento.data_inicio.strftime('%H:%M'),
                'duracao_minutos': evento.duracao_minutos,
                'data_inicio': evento.data_inicio.isoformat(),
                'data_fim': evento.data_fim.isoformat(),
                'local': evento.local,
                'responsavel': evento.responsavel,
                'email': evento.email,
                'telefone': evento.telefone,
                'cor': evento.cor,
                'notas': evento.notas,
            }
        })
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'mensagem': str(e)
        }, status=500)


def eventos_json(request):
    """Retornar todos os eventos em formato JSON (para fullcalendar ou similar)"""
    try:
        ano = int(request.GET.get('ano', timezone.now().year))
        mes = int(request.GET.get('mes', timezone.now().month))

        primeiro_dia = date(ano, mes, 1)
        ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])

        eventos = Evento.objects.filter(
            data_inicio__date__gte=primeiro_dia,
            data_inicio__date__lte=ultimo_dia
        ).order_by('data_inicio')

        dados = []
        for evento in eventos:
            dados.append({
                'id': evento.id,
                'title': evento.titulo,
                'start': evento.data_inicio.isoformat(),
                'end': evento.data_fim.isoformat(),
                'color': evento.cor,
                'extendedProps': {
                    'tipo': evento.tipo,
                    'local': evento.local,
                    'responsavel': evento.responsavel,
                    'descricao': evento.descricao,
                }
            })

        return JsonResponse({'sucesso': True, 'eventos': dados})
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'mensagem': str(e)
        }, status=500)


def evento_quick_add(request):
    """Adicionar evento rápido via AJAX"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            form = EventoQuickForm(dados)
            if form.is_valid():
                evento = form.save()
                return JsonResponse({
                    'sucesso': True,
                    'mensagem': 'Evento criado!',
                    'evento': {
                        'id': evento.id,
                        'titulo': evento.titulo,
                        'hora': evento.hora_inicio_formatada,
                    }
                })
            else:
                return JsonResponse({
                    'sucesso': False,
                    'erros': form.errors
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'mensagem': str(e)
            }, status=500)

    return JsonResponse({'sucesso': False}, status=405)
