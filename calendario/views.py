import calendar
import json
import logging
import uuid
from datetime import date, datetime, timedelta

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Evento
from .forms import EventoForm
from .google_calendar import GoogleCalendarError, criar_evento, excluir_evento

logger = logging.getLogger(__name__)


def _eventos_visiveis(user):
    return Evento.objects.filter(Q(compartilhado=True) | Q(criador=user))


@login_required
def calendario_view(request):
    hoje = timezone.now().date()

    try:
        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))
        if not 1 <= mes <= 12 or not 1900 <= ano <= 2100:
            raise ValueError
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
    eventos_mes = _eventos_visiveis(request.user).filter(
        data_inicio__date__gte=primeiro_dia,
        data_inicio__date__lte=ultimo_dia
    ).order_by('data_inicio')

    eventos_por_dia = {}
    for evento in eventos_mes:
        d = evento.data_inicio.day
        if d not in eventos_por_dia:
            eventos_por_dia[d] = []
        eventos_por_dia[d].append(evento)

    eventos_dia = _eventos_visiveis(request.user).filter(
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


def _proxima_data(dt, recorrencia, n):
    """Retorna a data dt deslocada n vezes conforme a recorrência."""
    if recorrencia == 'semanal':
        return dt + timedelta(weeks=n)
    elif recorrencia == 'mensal':
        mes_total = dt.month - 1 + n
        ano = dt.year + mes_total // 12
        mes = mes_total % 12 + 1
        dia = min(dt.day, calendar.monthrange(ano, mes)[1])
        return dt.replace(year=ano, month=mes, day=dia)
    elif recorrencia == 'anual':
        try:
            return dt.replace(year=dt.year + n)
        except ValueError:
            return dt.replace(year=dt.year + n, day=28)
    return None


@require_http_methods(["POST"])
@transaction.atomic
@login_required
def evento_criar(request):
    try:
        if request.content_type == 'application/json':
            dados = json.loads(request.body)
            form = EventoForm(dados)
        else:
            dados = request.POST.dict()
            form = EventoForm(dados)

        recorrencia = dados.get('recorrencia', 'nenhuma')
        data_limite_str = dados.get('data_limite_recorrencia')
        data_limite = None
        if data_limite_str:
            try:
                data_limite = datetime.strptime(data_limite_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if form.is_valid():
            evento = form.save(commit=False)
            evento.criador = request.user
            if recorrencia != 'nenhuma':
                evento.serie_id = str(uuid.uuid4())
            evento.save()

            if recorrencia != 'nenhuma':
                quantidade_repeticoes = dados.get('quantidade_repeticoes')
                try:
                    quantidade_repeticoes = int(quantidade_repeticoes) if quantidade_repeticoes else None
                except ValueError:
                    quantidade_repeticoes = None

                n = 1
                while True:
                    # Se tiver quantidade, para quando atingir o limite de repetições
                    if quantidade_repeticoes and n > quantidade_repeticoes:
                        break
                    
                    nova_dt = _proxima_data(evento.data_inicio, recorrencia, n)
                    
                    # Se tiver data limite, para quando atingir a data
                    if not nova_dt or (data_limite and nova_dt.date() > data_limite):
                        break
                    
                    # Se não tiver nem data limite nem quantidade, paramos para evitar loop infinito
                    # (Embora a lógica atual exija um dos dois ou pare por padrão)
                    if not data_limite and not quantidade_repeticoes:
                        # Limite de segurança de 1 ano se nada for especificado
                        if n >= 52 and recorrencia == 'semanal': break
                        if n >= 12 and recorrencia == 'mensal': break
                        if n >= 10 and recorrencia == 'anual': break

                    repeticao = Evento.objects.create(
                        titulo=evento.titulo,
                        criador=request.user,
                        compartilhado=evento.compartilhado,
                        data_inicio=nova_dt,
                        responsavel=evento.responsavel,
                        categoria=evento.categoria,
                        cor=evento.cor,
                        serie_id=evento.serie_id,
                        data_limite_recorrencia=data_limite
                    )
                    criar_evento(repeticao, request.user)
                    n += 1

            criar_evento(evento, request.user)

            msgs = {
                'semanal': f'Evento criado com recorrência semanal!',
                'mensal':  f'Evento criado com recorrência mensal!',
                'anual':   f'Evento criado com recorrência anual!',
            }
            return JsonResponse({
                'sucesso': True,
                'mensagem': msgs.get(recorrencia, 'Evento criado com sucesso!'),
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
    except GoogleCalendarError as exc:
        return JsonResponse({'sucesso': False, 'mensagem': str(exc)}, status=502)
    except Exception:
        logger.exception('Erro inesperado ao criar evento')
        return JsonResponse({'sucesso': False, 'mensagem': 'Erro interno ao criar evento'}, status=500)


@require_http_methods(["POST"])
@transaction.atomic
@login_required
def evento_editar(request, pk):
    try:
        evento = get_object_or_404(_eventos_visiveis(request.user), pk=pk)
        
        if request.content_type == 'application/json':
            dados = json.loads(request.body)
        else:
            dados = request.POST.dict()

        editar_serie = dados.get('editar_serie') == 'true' or dados.get('editar_serie') is True
        form = EventoForm(dados, instance=evento)

        if form.is_valid():
            if editar_serie and evento.serie_id:
                # Atualizar todos os eventos da série (apenas campos comuns)
                eventos_serie = Evento.objects.filter(serie_id=evento.serie_id)
                for ev in eventos_serie:
                    ev.titulo = form.cleaned_data['titulo']
                    ev.responsavel = form.cleaned_data['responsavel']
                    ev.categoria = form.cleaned_data['categoria']
                    ev.cor = form.cleaned_data['cor']
                    # Nota: Não alteramos a data/hora individual de cada um na série para não bagunçar o calendário
                    ev.save()
                msg = 'Série de eventos atualizada!'
            else:
                evento = form.save()
                msg = 'Evento atualizado com sucesso!'

            return JsonResponse({
                'sucesso': True,
                'mensagem': msg,
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
    except Exception:
        logger.exception('Erro inesperado ao editar evento %s', pk)
        return JsonResponse({'sucesso': False, 'mensagem': 'Erro interno ao editar evento'}, status=500)


@require_http_methods(["POST", "DELETE"])
@transaction.atomic
@login_required
def evento_excluir(request, pk):
    try:
        evento = get_object_or_404(_eventos_visiveis(request.user), pk=pk)
        titulo = evento.titulo
        
        excluir_serie = request.GET.get('excluir_serie') == 'true'
        if not excluir_serie and request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    dados = json.loads(request.body)
                    excluir_serie = dados.get('excluir_serie') == 'true'
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        if excluir_serie and evento.serie_id:
            eventos_serie = list(Evento.objects.filter(serie_id=evento.serie_id))
            count = len(eventos_serie)
            for item in eventos_serie:
                excluir_evento(item, request.user)
            Evento.objects.filter(pk__in=[item.pk for item in eventos_serie]).delete()
            return JsonResponse({'sucesso': True, 'mensagem': f'Série com {count} eventos excluída!'})
        
        excluir_evento(evento, request.user)
        evento.delete()
        return JsonResponse({'sucesso': True, 'mensagem': f'Evento "{titulo}" excluído!'})
    except GoogleCalendarError as exc:
        return JsonResponse({'sucesso': False, 'mensagem': str(exc)}, status=502)
    except Exception:
        logger.exception('Erro inesperado ao excluir evento %s', pk)
        return JsonResponse({'sucesso': False, 'mensagem': 'Erro interno ao excluir evento'}, status=500)


@login_required
def evento_detalhes(request, pk):
    try:
        evento = get_object_or_404(_eventos_visiveis(request.user), pk=pk)
        return JsonResponse({'sucesso': True, 'evento': _serializar(evento)})
    except Exception:
        logger.exception('Erro inesperado ao consultar evento %s', pk)
        return JsonResponse({'sucesso': False, 'mensagem': 'Erro interno ao consultar evento'}, status=500)


def _serializar(evento):
    return {
        'id': evento.id,
        'titulo': evento.titulo,
        'compartilhado': evento.compartilhado,
        'data': evento.data_inicio.strftime('%Y-%m-%d'),
        'hora': evento.data_inicio.strftime('%H:%M'),
        'responsavel': evento.responsavel,
        'categoria': evento.categoria,
        'cor': evento.cor,
        'serie_id': evento.serie_id,
        'data_limite': evento.data_limite_recorrencia.strftime('%Y-%m-%d') if evento.data_limite_recorrencia else None,
    }
