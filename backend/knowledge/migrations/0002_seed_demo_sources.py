from django.db import migrations

from knowledge.seed import seed_demo_sources


def forwards(apps, schema_editor):
    Document = apps.get_model("knowledge", "Document")
    DocumentChunk = apps.get_model("knowledge", "DocumentChunk")
    seed_demo_sources(Document, DocumentChunk)


def backwards(apps, schema_editor):
    Document = apps.get_model("knowledge", "Document")
    Document.objects.filter(
        slug__in=[
            "irembo-services",
            "education-research",
            "business-innovation",
            "responsible-ai",
            "rwanda-knowledge-blueprint",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
