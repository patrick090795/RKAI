from django.urls import path

from .views import (
    AnalyticsView,
    DocumentDetailView,
    DocumentIngestUrlView,
    DocumentListView,
    DocumentUploadView,
    FeedbackCreateView,
    HealthView,
    LowConfidenceAnswersView,
    QuestionAskView,
    QuestionHistoryView,
    UnansweredQuestionsView,
)


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("questions/ask/", QuestionAskView.as_view(), name="question-ask"),
    path("questions/history/", QuestionHistoryView.as_view(), name="question-history"),
    path("feedback/", FeedbackCreateView.as_view(), name="feedback-create"),
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("documents/upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("documents/ingest-url/", DocumentIngestUrlView.as_view(), name="document-ingest-url"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("admin/analytics/", AnalyticsView.as_view(), name="analytics"),
    path(
        "admin/unanswered-questions/",
        UnansweredQuestionsView.as_view(),
        name="unanswered-questions",
    ),
    path(
        "admin/low-confidence-answers/",
        LowConfidenceAnswersView.as_view(),
        name="low-confidence-answers",
    ),
]
