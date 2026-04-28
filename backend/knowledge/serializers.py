from django.utils.text import slugify
from rest_framework import serializers

from .models import Answer, Document, Feedback
from .rag import serialize_answer


class AskQuestionSerializer(serializers.Serializer):
    question_text = serializers.CharField(trim_whitespace=True)
    language = serializers.ChoiceField(
        choices=["Auto", "English", "Kinyarwanda"], default="Auto", required=False
    )


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "source_type",
            "source_url",
            "file",
            "category",
            "language",
            "status",
            "freshness",
            "is_active",
            "chunk_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at", "chunk_count"]

    def get_chunk_count(self, document):
        if hasattr(document, "chunk_total"):
            return document.chunk_total
        return document.chunks.count()


class DocumentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "title",
            "description",
            "source_type",
            "source_url",
            "file",
            "category",
            "language",
            "status",
            "freshness",
        ]
        extra_kwargs = {
            "source_type": {"required": False},
            "status": {"required": False},
            "freshness": {"required": False},
            "description": {"required": False},
            "source_url": {"required": False},
            "file": {"required": False},
        }

    def validate(self, attrs):
        source_type = attrs.get(
            "source_type",
            getattr(self.instance, "source_type", Document.SourceType.URL),
        )
        source_url = attrs.get("source_url", getattr(self.instance, "source_url", ""))

        if source_type == Document.SourceType.URL and not source_url:
            raise serializers.ValidationError(
                {"source_url": "This field is required when source_type is URL."}
            )

        return attrs

    def create(self, validated_data):
        base_slug = slugify(validated_data["title"]) or "source"
        slug = base_slug
        counter = 2
        while Document.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data["slug"] = slug
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["uploaded_by"] = request.user
        return super().create(validated_data)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "answer", "rating", "feedback_type", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)


class AnswerHistorySerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ["item"]

    def get_item(self, answer):
        return serialize_answer(answer)

    def to_representation(self, instance):
        return self.get_item(instance)
