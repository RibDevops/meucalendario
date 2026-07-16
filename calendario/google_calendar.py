from datetime import timedelta

from allauth.socialaccount.models import SocialToken
from django.conf import settings
from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GoogleCalendarError(Exception):
    pass


def _credentials_for(user):
    try:
        token = SocialToken.objects.select_related('account').get(
            account__user=user,
            account__provider='google',
        )
    except SocialToken.DoesNotExist as exc:
        raise GoogleCalendarError('Reconecte sua conta Google para autorizar a agenda.') from exc

    provider = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']
    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret or None,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=provider['client_id'],
        client_secret=provider['secret'],
        scopes=['https://www.googleapis.com/auth/calendar'],
    )
    if not credentials.valid:
        if not credentials.refresh_token:
            raise GoogleCalendarError('A autorização Google expirou; conecte a conta novamente.')
        credentials.refresh(Request())
        token.token = credentials.token
        if credentials.refresh_token:
            token.token_secret = credentials.refresh_token
        token.expires_at = credentials.expiry
        token.save(update_fields=['token', 'token_secret', 'expires_at'])
    return credentials


def criar_evento(evento, user):
    """Cria o evento no calendário familiar ou no calendário pessoal do usuário."""
    if not settings.GOOGLE_CALENDAR_SYNC_ENABLED:
        return evento

    calendar_id = settings.GOOGLE_FAMILY_CALENDAR_ID if evento.compartilhado else 'primary'
    if not calendar_id:
        raise GoogleCalendarError('O calendário familiar ainda não foi configurado.')

    inicio = evento.data_inicio
    if timezone.is_naive(inicio):
        inicio = timezone.make_aware(inicio, timezone.get_current_timezone())
    fim = inicio + timedelta(hours=1)
    body = {
        'summary': evento.titulo,
        'start': {'dateTime': inicio.isoformat(), 'timeZone': settings.TIME_ZONE},
        'end': {'dateTime': fim.isoformat(), 'timeZone': settings.TIME_ZONE},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }
    service = build('calendar', 'v3', credentials=_credentials_for(user), cache_discovery=False)
    resultado = service.events().insert(calendarId=calendar_id, body=body).execute()
    evento.google_event_id = resultado['id']
    evento.google_calendar_id = calendar_id
    evento.save(update_fields=['google_event_id', 'google_calendar_id'])
    return evento
