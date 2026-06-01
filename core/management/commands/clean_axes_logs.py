from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from axes.models import AccessLog, AccessAttempt


class Command(BaseCommand):
    help = "Delete old django-axes access logs and access attempts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Delete records older than this number of days.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - timedelta(days=days)

        deleted_logs, _ = AccessLog.objects.filter(attempt_time__lt=cutoff).delete()
        deleted_attempts, _ = AccessAttempt.objects.filter(attempt_time__lt=cutoff).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_logs} access logs and {deleted_attempts} access attempts older than {days} days."
            )
        )