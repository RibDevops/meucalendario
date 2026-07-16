from datetime import date, datetime

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Evento
from .views import _proxima_data


class RecorrenciaTests(TestCase):
    def test_recorrencia_mensal_ajusta_ultimo_dia(self):
        inicio = datetime(2026, 1, 31, 10, 0)
        self.assertEqual(_proxima_data(inicio, 'mensal', 1), datetime(2026, 2, 28, 10, 0))

    def test_recorrencia_anual_ajusta_ano_bissexto(self):
        inicio = datetime(2024, 2, 29, 10, 0)
        self.assertEqual(_proxima_data(inicio, 'anual', 1), datetime(2025, 2, 28, 10, 0))


class SegurancaEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user(username='teste', email='teste@example.com')
        self.client.force_login(self.user)

    def test_criacao_sem_csrf_e_rejeitada(self):
        resposta = self.client.post(
            reverse('evento_criar'),
            data={'titulo': 'Teste', 'data': '2026-07-20', 'hora': '10:00'},
        )
        self.assertEqual(resposta.status_code, 403)

    def test_mes_invalido_nao_causa_erro(self):
        client = Client()
        client.force_login(self.user)
        resposta = client.get(reverse('calendario'), {'ano': '2026', 'mes': '99'})
        self.assertEqual(resposta.status_code, 200)

    def test_calendario_exige_login(self):
        resposta = Client().get(reverse('calendario'))
        self.assertEqual(resposta.status_code, 302)


class EventoEndpointTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='teste', email='teste@example.com')
        self.client.force_login(self.user)

    def test_detalhes_serializa_evento(self):
        evento = Evento.objects.create(titulo='Consulta', criador=self.user, data_inicio='2026-07-20T10:00:00Z')
        resposta = self.client.get(reverse('evento_detalhes', args=[evento.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()['evento']['titulo'], 'Consulta')
