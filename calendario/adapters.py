from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpResponseForbidden


class AgendaSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Permite login somente às contas explicitamente convidadas."""

    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or '').strip().lower()
        if email not in settings.AGENDA_ALLOWED_EMAILS:
            raise ImmediateHttpResponse(
                HttpResponseForbidden('Esta conta Google ainda não foi convidada para a agenda.')
            )
