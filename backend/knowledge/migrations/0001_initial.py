import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(unique=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("source_type", models.CharField(choices=[("pdf", "PDF"), ("url", "URL"), ("policy", "Policy"), ("other", "Other")], default="url", max_length=32)),
                ("source_url", models.URLField(blank=True)),
                ("file", models.FileField(blank=True, null=True, upload_to="sources/")),
                ("category", models.CharField(max_length=100)),
                ("language", models.CharField(choices=[("English", "English"), ("Kinyarwanda", "Kinyarwanda"), ("Mixed", "Mixed")], default="English", max_length=32)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("pending_review", "Pending review"), ("approved", "Approved"), ("rejected", "Rejected"), ("archived", "Archived"), ("failed", "Failed")], default="pending_review", max_length=32)),
                ("freshness", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="uploaded_documents", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-updated_at", "title"],
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("detected_language", models.CharField(default="English", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="questions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="DocumentChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chunk_text", models.TextField()),
                ("embedding", models.JSONField(blank=True, null=True)),
                ("page_number", models.CharField(blank=True, max_length=32)),
                ("section_title", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="knowledge.document")),
            ],
            options={
                "ordering": ["document_id", "id"],
            },
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_text", models.TextField()),
                ("confidence_score", models.FloatField(default=0)),
                ("status", models.CharField(choices=[("answered", "Answered"), ("low_confidence", "Low confidence"), ("needs_review", "Needs review")], default="needs_review", max_length=32)),
                ("model_used", models.CharField(default="retrieval-demo", max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="knowledge.question")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Citation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_url", models.URLField(blank=True)),
                ("chunk_reference", models.CharField(blank=True, max_length=255)),
                ("page_number", models.CharField(blank=True, max_length=32)),
                ("section_title", models.CharField(blank=True, max_length=255)),
                ("excerpt", models.TextField(blank=True)),
                ("score", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("answer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="citations", to="knowledge.answer")),
                ("document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="citations", to="knowledge.document")),
            ],
            options={
                "ordering": ["answer_id", "-score"],
            },
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.CharField(choices=[("positive", "Positive"), ("negative", "Negative")], max_length=32)),
                ("feedback_type", models.CharField(choices=[("helpful", "Helpful"), ("wrong_answer", "Wrong answer"), ("missing_source", "Missing source"), ("language_issue", "Language issue"), ("outdated", "Outdated information"), ("other", "Other")], default="other", max_length=64)),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("answer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="feedback", to="knowledge.answer")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="feedback", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
