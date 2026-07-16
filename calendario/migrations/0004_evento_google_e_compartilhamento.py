from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calendario', '0003_evento_categoria_evento_data_limite_recorrencia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='criador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventos', to=settings.AUTH_USER_MODEL, verbose_name='Criador'),
        ),
        migrations.AddField(
            model_name='evento',
            name='compartilhado',
            field=models.BooleanField(default=True, verbose_name='Compartilhar'),
        ),
        migrations.AddField(
            model_name='evento',
            name='google_event_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='ID no Google Calendar'),
        ),
        migrations.AddField(
            model_name='evento',
            name='google_calendar_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='Calendário Google'),
        ),
    ]
