import os
import django
from datetime import datetime, date, timedelta

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from calendario.models import Evento
from calendario.views import _proxima_data

def testar_recorrencia():
    print("Iniciando testes de recorrência...\n")
    
    # Limpar eventos de teste anteriores
    Evento.objects.filter(titulo__startswith="TESTE-").delete()
    
    # 1. Testar lógica de próxima data
    dt_base = datetime(2026, 6, 1, 10, 0)
    
    # Semanal
    prox_semanal = _proxima_data(dt_base, 'semanal', 1)
    print(f"Semanal (1 semana): {prox_semanal}")
    assert prox_semanal.date() == date(2026, 6, 8)
    
    # Mensal
    prox_mensal = _proxima_data(dt_base, 'mensal', 1)
    print(f"Mensal (1 mês): {prox_mensal}")
    assert prox_mensal.date() == date(2026, 7, 1)
    
    # Anual
    prox_anual = _proxima_data(dt_base, 'anual', 1)
    print(f"Anual (1 ano): {prox_anual}")
    assert prox_anual.date() == date(2027, 6, 1)

    # 2. Testar criação de série no banco de dados
    print("\nTestando criação de série no banco...")
    titulo = "TESTE-RECORRENTE"
    data_inicio = datetime(2026, 6, 1, 14, 0)
    data_limite = date(2026, 6, 20) # Deve criar 3 eventos (dia 1, 8 e 15)
    serie_id = "serie-teste-123"
    
    # Criar o primeiro
    evento_pai = Evento.objects.create(
        titulo=titulo,
        data_inicio=data_inicio,
        serie_id=serie_id,
        data_limite_recorrencia=data_limite
    )
    
    # Simular a lógica da view para criar os filhos
    n = 1
    while True:
        nova_dt = _proxima_data(evento_pai.data_inicio, 'semanal', n)
        if not nova_dt or nova_dt.date() > data_limite:
            break
        
        Evento.objects.create(
            titulo=evento_pai.titulo,
            data_inicio=nova_dt,
            serie_id=evento_pai.serie_id,
            data_limite_recorrencia=data_limite
        )
        n += 1
    
    eventos = Evento.objects.filter(serie_id=serie_id).order_by('data_inicio')
    print(f"Eventos criados na série: {eventos.count()}")
    for e in eventos:
        print(f" - {e.titulo} em {e.data_inicio}")
    
    assert eventos.count() == 3
    print("\n✅ Teste de recorrência concluído com sucesso!")

if __name__ == "__main__":
    testar_recorrencia()
