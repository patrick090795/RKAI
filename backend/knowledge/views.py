from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, Document, Feedback, Question
from .ingest import ingest_document_content
from .permissions import IsStaffUser
from .rag import answer_question
from .serializers import (
    AnswerHistorySerializer,
    AdminLoginSerializer,
    AskQuestionSerializer,
    DocumentSerializer,
    DocumentStatusUpdateSerializer,
    DocumentWriteSerializer,
    FeedbackSerializer,
)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


def serialize_auth_payload(user, token=None):
    payload = {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.get_username(),
            "isStaff": user.is_staff,
            "isSuperuser": user.is_superuser,
        },
    }
    if token:
        payload["token"] = token
    return payload


class AuthLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user or not user.is_active:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(serialize_auth_payload(user, token=token.key))


class AuthLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(serialize_auth_payload(request.user))


class QuestionAskView(APIView):
    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = answer_question(
            serializer.validated_data["question_text"],
            serializer.validated_data.get("language", "Auto"),
            request.user,
        )
        return Response(result, status=status.HTTP_201_CREATED)


class QuestionHistoryView(generics.ListAPIView):
    serializer_class = AnswerHistorySerializer

    def get_queryset(self):
        if not (self.request.user and self.request.user.is_authenticated):
            return Answer.objects.none()

        queryset = Answer.objects.select_related("question").prefetch_related(
            "citations__document"
        )
        return queryset.filter(question__user=self.request.user).order_by("-created_at")[:50]


class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()


class DocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.annotate(chunk_total=Count("chunks"))
        category = self.request.query_params.get("category")
        document_status = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        if category:
            queryset = queryset.filter(category__iexact=category)
        if document_status:
            queryset = queryset.filter(status=document_status)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(category__icontains=search)
            )
        return queryset


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Document.objects.annotate(chunk_total=Count("chunks"))
    serializer_class = DocumentSerializer
    permission_classes = [IsStaffUser]


class DocumentUploadView(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DocumentWriteSerializer
    permission_classes = [IsStaffUser]

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.setdefault("source_type", Document.SourceType.PDF)
        data.setdefault("status", Document.Status.PENDING_REVIEW)
        data.setdefault("freshness", "Queued")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        try:
            chunk_count = ingest_document_content(document)
            if chunk_count == 0:
                document.status = Document.Status.FAILED
                document.freshness = "Ingestion failed: no extractable text."
                document.save(update_fields=["status", "freshness", "updated_at"])
        except Exception:
            document.status = Document.Status.FAILED
            document.freshness = "Ingestion failed: could not parse source."
            document.save(update_fields=["status", "freshness", "updated_at"])
        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class DocumentIngestUrlView(generics.CreateAPIView):
    serializer_class = DocumentWriteSerializer
    permission_classes = [IsStaffUser]

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.setdefault("source_type", Document.SourceType.URL)
        data.setdefault("status", Document.Status.PENDING_REVIEW)
        data.setdefault("freshness", "Queued")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        try:
            chunk_count = ingest_document_content(document)
            if chunk_count == 0:
                document.status = Document.Status.FAILED
                document.freshness = "Ingestion failed: no extractable text."
                document.save(update_fields=["status", "freshness", "updated_at"])
        except Exception:
            document.status = Document.Status.FAILED
            document.freshness = "Ingestion failed: could not parse source."
            document.save(update_fields=["status", "freshness", "updated_at"])
        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class DocumentStatusUpdateView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        serializer = DocumentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        next_status = serializer.validated_data["status"]
        document.status = next_status
        if next_status in {
            Document.Status.REJECTED,
            Document.Status.ARCHIVED,
            Document.Status.FAILED,
        }:
            document.is_active = False
        elif next_status == Document.Status.APPROVED:
            document.is_active = True

        document.save(update_fields=["status", "is_active", "updated_at"])
        return Response(DocumentSerializer(document).data)


class AnalyticsView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        return Response(
            {
                "documents": Document.objects.count(),
                "approvedDocuments": Document.objects.filter(
                    status=Document.Status.APPROVED
                ).count(),
                "queuedDocuments": Document.objects.exclude(
                    status=Document.Status.APPROVED
                ).count(),
                "questions": Question.objects.count(),
                "answers": Answer.objects.count(),
                "lowConfidenceAnswers": Answer.objects.exclude(
                    status=Answer.Status.ANSWERED
                ).count(),
                "feedback": Feedback.objects.count(),
            }
        )


class UnansweredQuestionsView(generics.ListAPIView):
    serializer_class = AnswerHistorySerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return (
            Answer.objects.select_related("question")
            .prefetch_related("citations__document")
            .filter(status=Answer.Status.NEEDS_REVIEW)
            .order_by("-created_at")
        )


class LowConfidenceAnswersView(generics.ListAPIView):
    serializer_class = AnswerHistorySerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return (
            Answer.objects.select_related("question")
            .prefetch_related("citations__document")
            .exclude(status=Answer.Status.ANSWERED)
            .order_by("-created_at")
        )
