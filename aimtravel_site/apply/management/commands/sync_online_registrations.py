from django.core.management.base import BaseCommand
from django.db.models import Q

from aimtravel_site.apply.models import Application
from aimtravel_site.apply.sheets_sync import sync_registration


class Command(BaseCommand):
    help = "Retry pending online registration exports without sending emails."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--all", action="store_true", dest="sync_all")

    def handle(self, *args, **options):
        applications = Application.objects.filter(currency="EUR")
        if not options["sync_all"]:
            applications = applications.filter(Q(sheets_synced_at__isnull=True) | ~Q(sheets_sync_error=""))
        applications = applications.select_related("contract_document").order_by("created_at")[:max(1, min(options["limit"], 1000))]
        total = successful = 0
        for application in applications:
            total += 1
            successful += bool(sync_registration(application))
        self.stdout.write(f"Google Sheets: {successful}/{total} synchronized.")
