const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: "application/json",
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function labelStatus(status) {
  const labels = {
    approved: "Approved",
    pending_review: "Pending review",
    draft: "Draft",
    rejected: "Rejected",
    archived: "Archived",
    failed: "Failed",
  };
  return labels[status] || status || "Pending review";
}

function labelSourceType(sourceType) {
  const labels = {
    pdf: "PDF",
    url: "URL",
    policy: "Policy",
    other: "Other",
  };
  return labels[sourceType] || sourceType || "URL";
}

export function mapDocument(document) {
  return {
    id: document.id ?? document.slug,
    slug: document.slug,
    title: document.title,
    category: document.category,
    language: document.language,
    sourceType: labelSourceType(document.source_type),
    sourceUrl: document.source_url || document.file || "",
    owner: "Knowledge API",
    status: labelStatus(document.status),
    freshness: document.freshness || "Queued",
    summary: document.description || "Source queued for review and ingestion.",
    chunks: [],
    chunkCount: document.chunk_count || 0,
  };
}

export async function checkApiHealth() {
  return apiFetch("/health/");
}

export async function fetchDocuments() {
  const documents = await apiFetch("/documents/");
  return documents.map(mapDocument);
}

export async function askBackendQuestion(questionText, language) {
  return apiFetch("/questions/ask/", {
    method: "POST",
    body: JSON.stringify({
      question_text: questionText,
      language,
    }),
  });
}

export async function fetchQuestionHistory() {
  return apiFetch("/questions/history/");
}

export async function sendFeedback({ answerId, rating, feedbackType, comment = "" }) {
  return apiFetch("/feedback/", {
    method: "POST",
    body: JSON.stringify({
      answer: answerId,
      rating,
      feedback_type: feedbackType,
      comment,
    }),
  });
}

export async function ingestUrlSource(source) {
  const document = await apiFetch("/documents/ingest-url/", {
    method: "POST",
    body: JSON.stringify({
      title: source.title,
      description: source.description,
      source_url: source.sourceUrl,
      category: source.category,
      language: source.language,
      freshness: "Queued",
    }),
  });
  return mapDocument(document);
}
