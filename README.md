# Sistema de Calendario com Django

Sistema completo de calendario e gerenciamento de eventos inspirado no Cal.com, com CRUD completo via modais.

![Calendario](https://img.shields.io/badge/Calendario-Django-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Django](https://img.shields.io/badge/Django-4.2+-darkgreen)

## Funcionalidades

### CRUD Completo via Modais
- **Criar**: Botao "Novo Evento" na coluna lateral + clique em horario disponivel
- **Editar**: Clique no card do evento ou botao de edicao
- **Excluir**: Botao de exclusao no card ou dentro do modal de edicao
- **Listar**: Visualizacao mensal com indicadores de eventos

### Layout em 3 Colunas (igual Cal.com)
1. **Coluna Esquerda**: Informacoes, estatisticas e botao de novo evento
2. **Coluna Central**: Calendario mensal com navegacao
3. **Coluna Direita**: Horarios do dia selecionado com eventos agendados

### Recursos
- Navegacao entre meses
- Selecao de dia com atualizacao dinamica
- Indicadores visuais de eventos nos dias
- Tooltips com detalhes dos eventos
- Sistema de Toast notifications
- Totalmente responsivo

## Instalacao

### 1. Clone ou extraia o projeto

```bash
cd calendario_django
```

### 2. Crie o ambiente virtual (recomendado)

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 5. Execute as migracoes

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie um superusuario (opcional, para acessar o admin)

```bash
python manage.py createsuperuser
```

### 7. Inicie o servidor

```bash
python manage.py runserver
```

### 8. Acesse no navegador

```
http://127.0.0.1:8000/
```

### 9. Acesse o Admin (opcional)

```
http://127.0.0.1:8000/admin/
```

## Estrutura do Projeto

```
calendario_django/
 agenda/
   __init__.py
   settings.py          # Configuracoes do Django
   urls.py              # URLs principais
   wsgi.py              # WSGI
 calendario/
   __init__.py
   admin.py             # Configuracao do Admin
   models.py            # Modelos: Evento, ConfiguracaoAgenda
   views.py             # Views: CRUD via AJAX
   urls.py              # URLs da app
   forms.py             # Formularios
   templatetags/        # Filtros customizados
   migrations/          # Migracoes
   templates/
     calendario/
       base.html        # Template base
       calendario.html  # Template principal
   static/
     css/
       calendario.css   # Estilos completos
     js/
       calendario.js    # JavaScript interativo
 manage.py              # Comando do Django
 requirements.txt       # Dependencias
 db.sqlite3             # Banco de dados
```

## APIs Endpoints

| Metodo | URL | Descricao |
|--------|-----|-----------|
| GET | `/` | Pagina principal do calendario |
| POST | `/evento/criar/` | Criar evento (JSON) |
| GET | `/evento/<id>/` | Detalhes do evento (JSON) |
| POST | `/evento/<id>/editar/` | Editar evento (JSON) |
| POST | `/evento/<id>/excluir/` | Excluir evento |
| POST | `/evento/quick-add/` | Criar evento rapido |
| GET | `/eventos/json/` | Listar eventos em JSON |

## Modelo de Dados

### Evento
| Campo | Tipo | Descricao |
|-------|------|-----------|
| titulo | CharField | Titulo do evento |
| descricao | TextField | Descricao detalhada |
| tipo | CharField | Tipo (reuniao, auditoria, consultoria, etc) |
| data_inicio | DateTimeField | Data e hora de inicio |
| data_fim | DateTimeField | Data e hora de termino |
| local | CharField | Local ou link |
| responsavel | CharField | Nome do responsavel |
| email | EmailField | E-mail de contato |
| telefone | CharField | Telefone |
| duracao_minutos | IntegerField | Duracao em minutos |
| cor | CharField | Cor em hexadecimal |
| notas | TextField | Notas internas |

## Como Usar

### Criar Evento
1. Clique no botao **"Novo Evento"** na coluna da esquerda
2. Preencha o formulario no modal
3. Clique em **"Salvar Evento"**

### Agendar Horario Rapido
1. Selecione um dia no calendario
2. Clique em um horario disponivel na coluna da direita
3. Preencha o titulo e clique em **"Agendar"**

### Editar Evento
1. Clique no card do evento na coluna da direita
2. Altere os campos desejados no modal
3. Clique em **"Atualizar"**

### Excluir Evento
- **Opcao 1**: Clique no icone de lixeira no card do evento
- **Opcao 2**: Dentro do modal de edicao, clique em **"Excluir"**

## Personalizacao

### Alterar cores
Edite o arquivo `static/css/calendario.css` e modifique as variaveis CSS no `:root`.

### Alterar horarios disponiveis
Edite a view `calendario_view` em `views.py` e ajuste o range de horas.

### Adicionar campos ao evento
1. Adicione o campo no `models.py`
2. Execute `makemigrations` e `migrate`
3. Adicione o campo no `forms.py`
4. Adicione o campo nos templates HTML

## Licenca

Este projeto e livre para uso e modificacao.
