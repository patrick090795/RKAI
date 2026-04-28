from django.contrib import admin

from .models import Answer, Citation, Document, DocumentChunk, Feedback, Question


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    fields = ("section_title", "page_number", "chunk_text")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "language", "status", "freshness", "updated_at")
    list_filter = ("status", "category", "language", "source_type", "is_active")
    search_fields = ("title", "description", "source_url")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [DocumentChunkInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "detected_language", "created_at")
    search_fields = ("question_text",)
    list_filter = ("detected_language",)


class CitationInline(admin.TabularInline):
    model = Citation
    extra = 0
    fields = ("document", "section_title", "page_number", "score")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "status", "confidence_score", "model_used", "created_at")
    list_filter = ("status", "model_used")
    search_fields = ("answer_text", "question__question_text")
    inlines = [CitationInline]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("rating", "feedback_type", "answer", "created_at")
    list_filter = ("rating", "feedback_type")
    search_fields = ("comment", "answer__question__question_text")
