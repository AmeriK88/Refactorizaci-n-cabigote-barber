from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone


class Command(BaseCommand):
    help = "Runs scheduled maintenance tasks."

    def handle(self, *args, **kwargs):

        self.stdout.write("Running appointment reminders...")
        call_command("enviar_recordatorios")

        # Execute Axes cleanup on the first day of each month to remove old failed login attempts
        if timezone.now().day == 1:
            self.stdout.write("Running axes cleanup...")
            call_command("clean_axes_logs", days=90)

        self.stdout.write(
            self.style.SUCCESS("Mantenimiento completado con éxito.")
        )