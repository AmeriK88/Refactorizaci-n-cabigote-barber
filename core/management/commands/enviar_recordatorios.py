from django.core.management.base import BaseCommand
from appointments.models import Cita
from core.utils import enviar_recordatorio_cita
from django.utils import timezone
from datetime import timedelta

# CRON JOB: REMINDER FOR APPOINTMENTS TOMORROW
class Command(BaseCommand):
    help = 'Sends email reminders for appointments scheduled for tomorrow.'

    def handle(self, *args, **kwargs):
        mañana_inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        mañana_fin = mañana_inicio.replace(hour=23, minute=59, second=59)

        citas = Cita.objects.filter(fecha__range=(mañana_inicio, mañana_fin))

        if not citas.exists():
            print('🚫 No hay citas para mañana.')
        else:
            for cita in citas:
                if cita.usuario and cita.usuario.email:
                    enviar_recordatorio_cita(cita.usuario.email, cita)
                    print(f'✅ Recordatorio enviado a {cita.usuario.email}')
