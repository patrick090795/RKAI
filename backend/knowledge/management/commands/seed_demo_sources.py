from django.core.management.base import BaseCommand

from knowledge.models import Document, DocumentChunk
from knowledge.seed import seed_demo_sources


class Command(BaseCommand):
    help = "Seed approved demo sources used by the MVP retriever."

    def handle(self, *args, **options):
        seed_demo_sources(Document, DocumentChunk)
        self.stdout.write(self.style.SUCCESS("Seeded demo sources."))
