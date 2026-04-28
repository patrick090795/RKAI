from django.conf import settings
from django.db import models


class Document(models.Model):
    class SourceType(models.TextChoices):
        PDF = "pdf", "PDF"
        URL = "url", "URL"
        POLICY = "policy", "Policy"
        OTHER = "other", "Other"

    class Language(models.TextChoices):
        ENGLISH = "English", "English"
        KINYARWANDA = "Kinyarwanda", "Kinyarwanda"
        MIXED = "Mixed", "Mixed"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        ARCHIVED = "archived", "Archived"
        FAILED = "failed", "Failed"

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_type = models.CharField(
        max_length=32, choices=SourceType.choices, default=SourceType.URL
    )
    source_url = models.URLField(blank=True)
    file = models.FileField(upload_to="sources/", blank=True, null=True)
    category = models.CharField(max_length=100)
    language = models.CharField(
        max_length=32, choices=Language.choices, default=Language.ENGLISH
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING_REVIEW
    )
    freshness = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "title"]

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_text = models.TextField()
    embedding = models.JSONField(blank=True, null=True)
    page_number = models.CharField(max_length=32, blank=True)
    section_title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document_id", "id"]

    def __str__(self):
        return f"{self.document.title}: {self.section_title or self.id}"


class Question(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="questions",
    )
    question_text = models.TextField()
    detected_language = models.CharField(max_length=32, default="English")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question_text[:80]


class Answer(models.Model):
    class Status(models.TextChoices):
        ANSWERED = "answered", "Answered"
        LOW_CONFIDENCE = "low_confidence", "Low confidence"
        NEEDS_REVIEW = "needs_review", "Needs review"

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    answer_text = models.TextField()
    confidence_score = models.FloatField(default=0)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.NEEDS_REVIEW
    )
    model_used = models.CharField(max_length=120, default="retrieval-demo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question_id}: {self.status}"


class Citation(models.Model):
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name="citations"
    )
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="citations"
    )
    source_url = models.URLField(blank=True)
    chunk_reference = models.CharField(max_length=255, blank=True)
    page_number = models.CharField(max_length=32, blank=True)
    section_title = models.CharField(max_length=255, blank=True)
    excerpt = models.TextField(blank=True)
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["answer_id", "-score"]

    def __str__(self):
        return f"{self.document.title} citation"


class Feedback(models.Model):
    class Rating(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEGATIVE = "negative", "Negative"

    class FeedbackType(models.TextChoices):
        HELPFUL = "helpful", "Helpful"
        WRONG_ANSWER = "wrong_answer", "Wrong answer"
        MISSING_SOURCE = "missing_source", "Missing source"
        LANGUAGE_ISSUE = "language_issue", "Language issue"
        OUTDATED = "outdated", "Outdated information"
        OTHER = "other", "Other"

    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name="feedback"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="feedback",
    )
    rating = models.CharField(max_length=32, choices=Rating.choices)
    feedback_type = models.CharField(
        max_length=64, choices=FeedbackType.choices, default=FeedbackType.OTHER
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}: {self.feedback_type}"
