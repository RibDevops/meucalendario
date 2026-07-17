# Continuidade do projeto Meu Calendário

Atualizado em: 16/07/2026

Este documento registra o ponto em que o trabalho parou e como continuar em outra máquina. Não coloque Client Secret, tokens, senhas ou a `DJANGO_SECRET_KEY` neste arquivo.

## Situação atual

- Repositório: `https://github.com/RibDevops/meucalendario.git`
- Branch: `main`
- Último commit observado: `fdd9d3d` (`v123`)
- Produção: `https://agenda.pythonanywhere.com/`
- Python do PythonAnywhere: 3.13
- Django em produção: 5.2.16
- Proprietário inicial: `andernet@gmail.com`
- Segunda pessoa autorizada: `eo.nathaliamaro@gmail.com`
- Proprietário usa iPhone; segunda pessoa usa Android.

## O que já foi implementado

- Saneamento das configurações de segurança do Django.
- Variáveis de ambiente para chave, debug, hosts e HTTPS.
- Proteção CSRF nos endpoints de escrita.
- Login Google com `django-allauth`.
- Lista de e-mails autorizados por configuração.
- Eventos compartilhados ou particulares.
- Opção "Compartilhar com a Agenda da Família" marcada por padrão.
- Eventos particulares visíveis somente para o criador.
- Base da criação de eventos pela Google Calendar API.
- Lembretes padrão de 1 dia e 30 minutos.
- Migração `0004_evento_google_e_compartilhamento.py`.
- Testes automatizados; seis testes estavam passando na última validação.
- Dependência explícita de `PyJWT[crypto]`, necessária para o login Google.
- `ALLOWED_HOSTS` configurado para `agenda.pythonanywhere.com`.

Ainda falta sincronizar edições e exclusões com o Google Calendar e criar a interface de convite para novas pessoas.

## Ponto exato em que paramos

No Google Cloud, a tela **Criar credenciais** estava aberta com:

- API: Google Calendar API
- Dados acessados: Dados do usuário

Essa seleção está correta. O próximo passo é clicar em **Avançar** e concluir a configuração abaixo.

## Continuar a configuração do Google Cloud

### 1. Consentimento OAuth

Use:

- Nome: `Agenda da Família`
- E-mail de suporte: `andernet@gmail.com`
- Público: Externo/External
- E-mail de contato: `andernet@gmail.com`

Adicione como usuários de teste:

- `andernet@gmail.com`
- `eo.nathaliamaro@gmail.com`

Escopos necessários:

- `openid`
- `email`
- `profile`
- `https://www.googleapis.com/auth/calendar`

### 2. Cliente OAuth

Crie um cliente do tipo **Aplicativo da Web** com o nome `Agenda PythonAnywhere`.

Origem JavaScript autorizada, sem barra final:

```text
https://agenda.pythonanywhere.com
```

URI de redirecionamento autorizada, com barra final:

```text
https://agenda.pythonanywhere.com/accounts/google/login/callback/
```

Guarde o Client ID e o Client Secret fora do repositório.

### 3. Calendário familiar

No Google Calendar de `andernet@gmail.com`:

1. Crie uma agenda chamada `Agenda da Família`.
2. Compartilhe com `eo.nathaliamaro@gmail.com`.
3. Dê permissão para alterar eventos.
4. Abra **Configurações e compartilhamento → Integrar agenda**.
5. Copie o campo **ID da agenda**, não o endereço iCal.

## Configuração no PythonAnywhere

Edite `/var/www/agenda_pythonanywhere_com_wsgi.py`. Antes de `get_wsgi_application()`, defina:

```python
import os

os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "agenda.pythonanywhere.com"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://agenda.pythonanywhere.com"
os.environ["DJANGO_SECRET_KEY"] = "VALOR-SECRETO-FORA-DO-GIT"

os.environ["AGENDA_OWNER_EMAIL"] = "andernet@gmail.com"
os.environ["AGENDA_ALLOWED_EMAILS"] = "andernet@gmail.com,eo.nathaliamaro@gmail.com"

os.environ["GOOGLE_OAUTH_CLIENT_ID"] = "VALOR-FORA-DO-GIT"
os.environ["GOOGLE_OAUTH_CLIENT_SECRET"] = "VALOR-FORA-DO-GIT"
os.environ["GOOGLE_FAMILY_CALENDAR_ID"] = "ID-DA-AGENDA-FAMILIAR"
os.environ["GOOGLE_CALENDAR_SYNC_ENABLED"] = "True"
```

O arquivo `.env.example` é somente um modelo. O projeto não carrega esse arquivo automaticamente.

Depois, no console Bash do PythonAnywhere:

```bash
cd /home/agenda/meucalendario
python3.13 -m pip install --user -r requirements.txt
python3.13 manage.py migrate
python3.13 manage.py check
python3.13 manage.py test
```

Na aba **Web**, clique em **Reload agenda.pythonanywhere.com**.

## Abrir em outra máquina

```bash
git clone https://github.com/RibDevops/meucalendario.git
cd meucalendario
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver
```

Para desenvolvimento local, as credenciais OAuth precisam ter também um callback local cadastrado no Google Cloud:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

As variáveis podem ser exportadas no terminal antes de iniciar o Django. Não use valores reais em arquivos versionados.

## Checklist depois do primeiro login

1. Entrar como `andernet@gmail.com`.
2. Aceitar o acesso solicitado ao Google Calendar.
3. Criar um evento compartilhado e confirmar que apareceu na Agenda da Família.
4. Confirmar os lembretes de 1 dia e 30 minutos.
5. Entrar como `eo.nathaliamaro@gmail.com` e confirmar acesso.
6. Criar um evento particular com a opção de compartilhamento desmarcada.
7. Confirmar que o evento particular não aparece para a outra conta.

## Erros já encontrados

- `ModuleNotFoundError: No module named 'jwt'`: instalar novamente `requirements.txt`; `PyJWT[crypto]` já está declarado.
- `DisallowedHost`: configurar `DJANGO_ALLOWED_HOSTS=agenda.pythonanywhere.com` e recarregar o site.
- OAuth `invalid_request`: normalmente Client ID vazio ou configuração OAuth incompleta.
- OAuth `redirect_uri_mismatch`: conferir exatamente o callback com HTTPS e barra final.
