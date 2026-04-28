import {
  AlertCircle,
  BarChart3,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Database,
  FileText,
  Flag,
  Globe2,
  Languages,
  Link,
  LockKeyhole,
  MessageSquare,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Upload,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  askBackendQuestion,
  checkApiHealth,
  fetchDocuments,
  fetchQuestionHistory,
  ingestUrlSource,
  sendFeedback,
} from "./api";

const FALLBACK = "I am not sure based on the available trusted sources.";

const navItems = [
  { id: "ask", label: "Ask AI", icon: MessageSquare },
  { id: "library", label: "Library", icon: BookOpen },
  { id: "admin", label: "Admin", icon: ShieldCheck },
  { id: "quality", label: "Quality", icon: BarChart3 },
];

const sourceDocuments = [
  {
    id: "irembo-services",
    title: "IremboGov public services overview",
    category: "Public services",
    language: "English",
    sourceType: "URL",
    sourceUrl: "https://www.irembo.gov.rw/",
    owner: "Government service portal",
    status: "Approved",
    freshness: "Current",
    summary:
      "Guidance for finding and starting public-service applications through Rwanda's digital service portal.",
    chunks: [
      {
        section: "Finding services",
        page: "Portal",
        text:
          "IremboGov is used as a public digital gateway for many government services in Rwanda. A user should search for a service, read the requirements shown for that service, follow the listed steps, and use the official service page for the most current fees, documents, and eligibility details.",
        keywords: [
          "irembo",
          "public",
          "service",
          "services",
          "documents",
          "application",
          "certificate",
          "permit",
          "government",
          "citizen",
          "portal",
        ],
      },
      {
        section: "Trust and next steps",
        page: "Portal",
        text:
          "When a public-service question depends on current requirements, the assistant should cite the official service page and avoid guessing. Users should confirm final instructions on the source page or with the responsible institution.",
        keywords: [
          "requirements",
          "fees",
          "eligibility",
          "current",
          "source",
          "institution",
          "official",
          "trusted",
        ],
      },
    ],
  },
  {
    id: "education-research",
    title: "Education and research information guide",
    category: "Education",
    language: "English",
    sourceType: "PDF",
    sourceUrl: "https://www.mineduc.gov.rw/",
    owner: "Education sector source",
    status: "Approved",
    freshness: "Review monthly",
    summary:
      "Seed material for education, scholarship, university, research, and institutional knowledge questions.",
    chunks: [
      {
        section: "Research discovery",
        page: "4",
        text:
          "Students and researchers need a knowledge library that can surface relevant documents, summarize trusted materials, preserve citations, and help identify source gaps for human review.",
        keywords: [
          "student",
          "students",
          "research",
          "researcher",
          "researchers",
          "university",
          "education",
          "scholarship",
          "documents",
          "library",
          "summaries",
        ],
      },
      {
        section: "Language inclusion",
        page: "7",
        text:
          "Kinyarwanda support should begin with language detection, translated or normalized queries, an expanding glossary, and human review for answers that may affect public understanding.",
        keywords: [
          "kinyarwanda",
          "language",
          "translation",
          "glossary",
          "review",
          "english",
          "local",
          "normalize",
        ],
      },
    ],
  },
  {
    id: "business-innovation",
    title: "Business and innovation support directory",
    category: "Innovation",
    language: "English",
    sourceType: "URL",
    sourceUrl: "https://rdb.rw/",
    owner: "Business ecosystem source",
    status: "Approved",
    freshness: "Current",
    summary:
      "Starter material for business registration, investment guidance, innovation ecosystem, and funding discovery.",
    chunks: [
      {
        section: "Ecosystem navigation",
        page: "Directory",
        text:
          "Ecosystem builders and institutions need a source-grounded assistant that can help users discover business, innovation, funding, and collaboration information while linking back to the responsible organizations.",
        keywords: [
          "business",
          "innovation",
          "startup",
          "funding",
          "grant",
          "collaboration",
          "ecosystem",
          "investment",
          "rdb",
          "company",
        ],
      },
      {
        section: "Governance",
        page: "Directory",
        text:
          "Documents used for business or innovation guidance should have categories, approval status, source links, and freshness checks so administrators can remove outdated or untrusted material.",
        keywords: [
          "admin",
          "approval",
          "outdated",
          "category",
          "source",
          "status",
          "freshness",
          "document",
        ],
      },
    ],
  },
  {
    id: "responsible-ai",
    title: "Responsible AI operating rules",
    category: "Governance",
    language: "English",
    sourceType: "Policy",
    sourceUrl: "internal://responsible-ai-rules",
    owner: "Platform governance",
    status: "Approved",
    freshness: "Always active",
    summary:
      "Rules for grounded answers, citations, privacy, role-based access, and low-confidence review.",
    chunks: [
      {
        section: "Non-negotiable answer rule",
        page: "6",
        text:
          "The assistant should never answer without enough trusted evidence. If retrieval is weak, it must say: I am not sure based on the available trusted sources.",
        keywords: [
          "fallback",
          "not sure",
          "trusted",
          "evidence",
          "guess",
          "uncertain",
          "confidence",
          "responsible",
          "safety",
        ],
      },
      {
        section: "Security controls",
        page: "6",
        text:
          "The MVP should use role-based access control for admin actions, avoid collecting sensitive personal data, keep secrets out of source control, validate inputs, and track feedback for human review.",
        keywords: [
          "security",
          "privacy",
          "roles",
          "admin",
          "feedback",
          "review",
          "secrets",
          "validation",
          "sensitive",
        ],
      },
    ],
  },
  {
    id: "rwanda-knowledge-blueprint",
    title: "Rwanda Knowledge AI Assistant design blueprint",
    category: "Platform design",
    language: "English",
    sourceType: "PDF",
    sourceUrl: "local://Rwanda_Knowledge_AI_Assistant_Design_Blueprint.pdf",
    owner: "Project team",
    status: "Approved",
    freshness: "Planning draft",
    summary:
      "The funder-ready design blueprint that defines the MVP, architecture, RAG workflow, and future roadmap.",
    chunks: [
      {
        section: "MVP goal",
        page: "1",
        text:
          "The MVP should be a working demo that answers from trusted sources with citations and basic English and Kinyarwanda support.",
        keywords: [
          "mvp",
          "demo",
          "citations",
          "english",
          "kinyarwanda",
          "trusted",
          "sources",
          "working",
        ],
      },
      {
        section: "Recommended stack",
        page: "5",
        text:
          "The recommended stack is React with Tailwind CSS, Django REST Framework, PostgreSQL with pgvector, Celery, Redis, a RAG pipeline, Docker, and cloud deployment.",
        keywords: [
          "react",
          "tailwind",
          "django",
          "postgresql",
          "pgvector",
          "celery",
          "redis",
          "docker",
          "cloud",
          "architecture",
          "stack",
        ],
      },
    ],
  },
];

const starterQuestions = [
  "How should I find trusted public service information?",
  "What should the assistant do when it cannot find evidence?",
  "How will Kinyarwanda support work in the MVP?",
  "What is the recommended technical stack?",
];

const kinyarwandaHints = [
  "amakuru",
  "muraho",
  "serivisi",
  "uburezi",
  "ubushakashatsi",
  "ikinyarwanda",
  "inyandiko",
  "u rwanda",
  "urwanda",
  "icyangombwa",
  "kwiyandikisha",
  "ubuyobozi",
  "ubucuruzi",
];

function normalize(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

function detectLanguage(question, selectedLanguage) {
  if (selectedLanguage !== "Auto") {
    return selectedLanguage;
  }

  const lowerQuestion = question.toLowerCase();
  return kinyarwandaHints.some((hint) => lowerQuestion.includes(hint))
    ? "Kinyarwanda"
    : "English";
}

function scoreChunk(questionTokens, chunk, document) {
  const searchable = normalize(
    `${document.title} ${document.category} ${document.summary} ${chunk.text} ${chunk.keywords.join(" ")}`,
  );
  const searchableSet = new Set(searchable);
  const matches = questionTokens.filter((token) => searchableSet.has(token));
  const keywordMatches = chunk.keywords.filter((keyword) =>
    questionTokens.some((token) => keyword.includes(token) || token.includes(keyword)),
  );

  return matches.length + keywordMatches.length * 2;
}

function retrieveEvidence(question) {
  const questionTokens = normalize(question).filter((token) => token.length > 2);
  if (questionTokens.length === 0) {
    return [];
  }

  return sourceDocuments
    .flatMap((document) =>
      document.chunks.map((chunk) => ({
        document,
        chunk,
        score: scoreChunk(questionTokens, chunk, document),
      })),
    )
    .filter((item) => item.document.status === "Approved" && item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
}

function confidenceFromEvidence(evidence) {
  if (!evidence.length) return 0;
  const topScore = evidence[0].score;
  const supportScore = evidence.reduce((sum, item) => sum + item.score, 0);
  return Math.min(0.94, 0.38 + topScore * 0.08 + supportScore * 0.025);
}

function answerFromEvidence(question, selectedLanguage) {
  const language = detectLanguage(question, selectedLanguage);
  const evidence = retrieveEvidence(question);
  const confidence = confidenceFromEvidence(evidence);
  const hasEvidence = evidence.length > 0 && confidence >= 0.58;

  if (!hasEvidence) {
    return {
      id: crypto.randomUUID(),
      question,
      answer: FALLBACK,
      language,
      confidence,
      citations: [],
      status: "Needs review",
      createdAt: new Date().toISOString(),
    };
  }

  const leadingCitation = evidence[0];
  const supportingCitation = evidence[1];
  const isKinyarwanda = language === "Kinyarwanda";
  const answer = isKinyarwanda
    ? [
        "Dushingiye ku masoko yemejwe muri iyi demo, igisubizo kigomba kuva ku nyandiko zizewe kandi kigatanga aho amakuru yavuye.",
        leadingCitation.chunk.text,
        supportingCitation
          ? `Andi makuru ashyigikira iki gisubizo agaragara muri "${supportingCitation.document.title}".`
          : "Niba amakuru adahagije, sisitemu igomba gusaba isuzuma ry'umuntu.",
      ].join(" ")
    : [
        "Based on the approved sources in this demo, the assistant should answer only from retrieved evidence and keep the source visible to the user.",
        leadingCitation.chunk.text,
        supportingCitation
          ? `A supporting source also says: ${supportingCitation.chunk.text}`
          : "When the evidence is thin, the answer should be routed for human review.",
      ].join(" ");

  return {
    id: crypto.randomUUID(),
    question,
    answer,
    language,
    confidence,
    citations: evidence.map(({ document, chunk, score }) => ({
      documentId: document.id,
      title: document.title,
      category: document.category,
      sourceUrl: document.sourceUrl,
      page: chunk.page,
      section: chunk.section,
      excerpt: chunk.text,
      score,
    })),
    status: confidence >= 0.74 ? "Answered" : "Low confidence",
    createdAt: new Date().toISOString(),
  };
}

function App() {
  const [activeView, setActiveView] = useState("ask");
  const [question, setQuestion] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("Auto");
  const [apiStatus, setApiStatus] = useState("checking");
  const [answers, setAnswers] = useState(() => [
    answerFromEvidence("What should the assistant do when it cannot find evidence?", "English"),
  ]);
  const [feedback, setFeedback] = useState([]);
  const [libraryQuery, setLibraryQuery] = useState("");
  const [libraryCategory, setLibraryCategory] = useState("All");
  const [adminDocuments, setAdminDocuments] = useState(sourceDocuments);
  const [ingestForm, setIngestForm] = useState({
    title: "",
    sourceUrl: "",
    category: "Public services",
    language: "English",
  });

  useEffect(() => {
    let isMounted = true;

    async function hydrateFromApi() {
      try {
        await checkApiHealth();
        const [documents, history] = await Promise.all([
          fetchDocuments(),
          fetchQuestionHistory().catch(() => []),
        ]);
        if (!isMounted) return;
        setApiStatus("online");
        if (documents.length) {
          setAdminDocuments(documents);
        }
        if (history.length) {
          setAnswers(history);
        }
      } catch {
        if (isMounted) {
          setApiStatus("offline");
        }
      }
    }

    hydrateFromApi();
    return () => {
      isMounted = false;
    };
  }, []);

  const latestAnswer = answers[0];
  const lowConfidenceAnswers = answers.filter(
    (item) => item.status !== "Answered" || item.confidence < 0.74,
  );

  const categories = useMemo(
    () => ["All", ...new Set(adminDocuments.map((document) => document.category))],
    [adminDocuments],
  );

  const filteredDocuments = useMemo(() => {
    const tokens = normalize(libraryQuery);
    return adminDocuments.filter((document) => {
      const matchesCategory =
        libraryCategory === "All" || document.category === libraryCategory;
      const haystack = normalize(`${document.title} ${document.summary} ${document.category}`);
      const matchesQuery =
        tokens.length === 0 || tokens.every((token) => haystack.includes(token));
      return matchesCategory && matchesQuery;
    });
  }, [adminDocuments, libraryCategory, libraryQuery]);

  async function submitQuestion(event) {
    event.preventDefault();
    const cleanQuestion = question.trim();
    if (!cleanQuestion) return;

    let result;
    try {
      result = await askBackendQuestion(cleanQuestion, selectedLanguage);
      setApiStatus("online");
    } catch {
      result = answerFromEvidence(cleanQuestion, selectedLanguage);
      setApiStatus("offline");
    }

    setAnswers((current) => [result, ...current]);
    setQuestion("");
    setActiveView("ask");
  }

  async function submitFeedback(answer, rating, feedbackType) {
    const feedbackItem = {
      id: crypto.randomUUID(),
      answerId: answer.id,
      question: answer.question,
      rating,
      feedbackType,
      createdAt: new Date().toISOString(),
    };

    setFeedback((current) => [
      feedbackItem,
      ...current,
    ]);

    if (Number.isInteger(answer.id)) {
      try {
        await sendFeedback({ answerId: answer.id, rating, feedbackType });
        setApiStatus("online");
      } catch {
        setApiStatus("offline");
      }
    }
  }

  async function addAdminDocument(event) {
    event.preventDefault();
    if (!ingestForm.title.trim()) return;
    const hasSourceUrl = Boolean(ingestForm.sourceUrl.trim());

    const pendingDocument = {
      id: `queued-${Date.now()}`,
      title: ingestForm.title.trim(),
      category: ingestForm.category,
      language: ingestForm.language,
      sourceType: hasSourceUrl ? "URL" : "PDF",
      sourceUrl: hasSourceUrl ? ingestForm.sourceUrl.trim() : "upload://pending-file",
      owner: "Admin upload",
      status: "Pending review",
      freshness: "Queued",
      summary:
        "New source queued for extraction, chunking, embedding, approval, and freshness review.",
      chunks: [],
    };

    if (!hasSourceUrl) {
      setAdminDocuments((current) => [pendingDocument, ...current]);
      setIngestForm({
        title: "",
        sourceUrl: "",
        category: "Public services",
        language: "English",
      });
      return;
    }

    try {
      const savedDocument = await ingestUrlSource({
        title: ingestForm.title.trim(),
        description:
          "New source queued for extraction, chunking, embedding, approval, and freshness review.",
        sourceUrl: ingestForm.sourceUrl.trim(),
        category: ingestForm.category,
        language: ingestForm.language,
      });
      setAdminDocuments((current) => [savedDocument, ...current]);
      setApiStatus("online");
    } catch {
      setAdminDocuments((current) => [pendingDocument, ...current]);
      setApiStatus("offline");
    }

    setIngestForm({
      title: "",
      sourceUrl: "",
      category: "Public services",
      language: "English",
    });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            <Flag size={22} />
          </div>
          <div>
            <p className="eyebrow">Rwanda Knowledge</p>
            <h1>AI Assistant</h1>
          </div>
        </div>

        <nav className="nav-list" aria-label="Primary">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                className={activeView === item.id ? "nav-item active" : "nav-item"}
                key={item.id}
                onClick={() => setActiveView(item.id)}
                type="button"
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="trust-panel">
          <ShieldCheck size={18} />
          <div>
            <strong>Grounded mode</strong>
            <span>Approved sources only</span>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">MVP prototype</p>
            <h2>{viewTitle(activeView)}</h2>
          </div>
          <div className="system-signals" aria-label="System status">
            <span className={`api-status ${apiStatus}`}>
              <Database size={16} />
              {apiStatus === "online"
                ? "API connected"
                : apiStatus === "checking"
                  ? "Checking API"
                  : "Demo fallback"}
            </span>
            <span>
              <CheckCircle2 size={16} />
              {adminDocuments.filter((doc) => doc.status === "Approved").length} approved
            </span>
            <span>
              <Languages size={16} />
              EN / RW
            </span>
            <span>
              <LockKeyhole size={16} />
              Admin gated
            </span>
          </div>
        </header>

        {activeView === "ask" && (
          <AskView
            question={question}
            setQuestion={setQuestion}
            selectedLanguage={selectedLanguage}
            setSelectedLanguage={setSelectedLanguage}
            submitQuestion={submitQuestion}
            latestAnswer={latestAnswer}
            answers={answers}
            submitFeedback={submitFeedback}
            starterQuestions={starterQuestions}
          />
        )}

        {activeView === "library" && (
          <LibraryView
            documents={filteredDocuments}
            libraryQuery={libraryQuery}
            setLibraryQuery={setLibraryQuery}
            libraryCategory={libraryCategory}
            setLibraryCategory={setLibraryCategory}
            categories={categories}
          />
        )}

        {activeView === "admin" && (
          <AdminView
            documents={adminDocuments}
            ingestForm={ingestForm}
            setIngestForm={setIngestForm}
            addAdminDocument={addAdminDocument}
          />
        )}

        {activeView === "quality" && (
          <QualityView
            answers={answers}
            feedback={feedback}
            lowConfidenceAnswers={lowConfidenceAnswers}
          />
        )}
      </main>
    </div>
  );
}

function viewTitle(activeView) {
  switch (activeView) {
    case "library":
      return "Knowledge Library";
    case "admin":
      return "Source Governance";
    case "quality":
      return "Feedback and Evaluation";
    default:
      return "Ask from trusted sources";
  }
}

function AskView({
  question,
  setQuestion,
  selectedLanguage,
  setSelectedLanguage,
  submitQuestion,
  latestAnswer,
  answers,
  submitFeedback,
  starterQuestions,
}) {
  return (
    <section className="ask-grid">
      <div className="ask-primary">
        <form className="question-panel" onSubmit={submitQuestion}>
          <label htmlFor="question">Question</label>
          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about Rwanda public services, education, research, innovation, or platform design..."
            rows={5}
          />
          <div className="question-actions">
            <label className="select-label" htmlFor="language">
              <Languages size={16} />
              <select
                id="language"
                value={selectedLanguage}
                onChange={(event) => setSelectedLanguage(event.target.value)}
              >
                <option>Auto</option>
                <option>English</option>
                <option>Kinyarwanda</option>
              </select>
            </label>
            <button type="submit" className="primary-action">
              <Send size={18} />
              Ask
            </button>
          </div>
        </form>

        {latestAnswer && (
          <article className="answer-panel">
            <div className="answer-header">
              <div>
                <p className="eyebrow">Answer</p>
                <h3>{latestAnswer.question}</h3>
              </div>
              <ConfidenceBadge confidence={latestAnswer.confidence} status={latestAnswer.status} />
            </div>
            <p className="answer-text">{latestAnswer.answer}</p>
            <div className="feedback-row" aria-label="Feedback">
              <button
                type="button"
                title="Helpful"
                onClick={() => submitFeedback(latestAnswer, "positive", "helpful")}
              >
                <ThumbsUp size={17} />
                Helpful
              </button>
              <button
                type="button"
                title="Not helpful"
                onClick={() => submitFeedback(latestAnswer, "negative", "wrong_answer")}
              >
                <ThumbsDown size={17} />
                Flag
              </button>
            </div>
            <CitationList citations={latestAnswer.citations} />
          </article>
        )}
      </div>

      <aside className="ask-secondary">
        <div className="section-heading">
          <Sparkles size={18} />
          <h3>Try a question</h3>
        </div>
        <div className="starter-list">
          {starterQuestions.map((starter) => (
            <button
              key={starter}
              type="button"
              onClick={() => setQuestion(starter)}
              title={starter}
            >
              <span>{starter}</span>
              <ChevronRight size={16} />
            </button>
          ))}
        </div>

        <div className="history-panel">
          <div className="section-heading">
            <Database size={18} />
            <h3>Recent answers</h3>
          </div>
          <div className="history-list">
            {answers.slice(0, 5).map((answer) => (
              <div className="history-item" key={answer.id}>
                <span>{answer.question}</span>
                <ConfidenceBadge confidence={answer.confidence} status={answer.status} compact />
              </div>
            ))}
          </div>
        </div>
      </aside>
    </section>
  );
}

function LibraryView({
  documents,
  libraryQuery,
  setLibraryQuery,
  libraryCategory,
  setLibraryCategory,
  categories,
}) {
  return (
    <section className="content-stack">
      <div className="toolbar">
        <label className="search-field" htmlFor="library-search">
          <Search size={17} />
          <input
            id="library-search"
            value={libraryQuery}
            onChange={(event) => setLibraryQuery(event.target.value)}
            placeholder="Search title, category, or summary"
          />
        </label>
        <label className="select-label" htmlFor="category-filter">
          <BookOpen size={16} />
          <select
            id="category-filter"
            value={libraryCategory}
            onChange={(event) => setLibraryCategory(event.target.value)}
          >
            {categories.map((category) => (
              <option key={category}>{category}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="document-grid">
        {documents.map((document) => (
          <DocumentCard document={document} key={document.id} />
        ))}
      </div>
    </section>
  );
}

function AdminView({ documents, ingestForm, setIngestForm, addAdminDocument }) {
  const approved = documents.filter((document) => document.status === "Approved").length;
  const pending = documents.filter((document) => document.status !== "Approved").length;

  return (
    <section className="admin-layout">
      <div className="metric-row">
        <MetricCard icon={CheckCircle2} label="Approved sources" value={approved} />
        <MetricCard icon={Upload} label="Queued for review" value={pending} />
        <MetricCard icon={Globe2} label="Source categories" value={new Set(documents.map((d) => d.category)).size} />
      </div>

      <div className="admin-grid">
        <form className="ingest-panel" onSubmit={addAdminDocument}>
          <div className="section-heading">
            <Upload size={18} />
            <h3>Add trusted source</h3>
          </div>

          <label htmlFor="source-title">Title</label>
          <input
            id="source-title"
            value={ingestForm.title}
            onChange={(event) =>
              setIngestForm((current) => ({ ...current, title: event.target.value }))
            }
            placeholder="Document or page title"
          />

          <label htmlFor="source-url">URL</label>
          <input
            id="source-url"
            value={ingestForm.sourceUrl}
            onChange={(event) =>
              setIngestForm((current) => ({ ...current, sourceUrl: event.target.value }))
            }
            placeholder="https://..."
          />

          <div className="form-split">
            <label htmlFor="source-category">
              Category
              <select
                id="source-category"
                value={ingestForm.category}
                onChange={(event) =>
                  setIngestForm((current) => ({ ...current, category: event.target.value }))
                }
              >
                <option>Public services</option>
                <option>Education</option>
                <option>Innovation</option>
                <option>Governance</option>
                <option>Platform design</option>
              </select>
            </label>
            <label htmlFor="source-language">
              Language
              <select
                id="source-language"
                value={ingestForm.language}
                onChange={(event) =>
                  setIngestForm((current) => ({ ...current, language: event.target.value }))
                }
              >
                <option>English</option>
                <option>Kinyarwanda</option>
                <option>Mixed</option>
              </select>
            </label>
          </div>

          <button type="submit" className="primary-action">
            <Upload size={18} />
            Queue source
          </button>
        </form>

        <div className="queue-panel">
          <div className="section-heading">
            <FileText size={18} />
            <h3>Ingestion queue</h3>
          </div>
          <div className="queue-list">
            {documents.map((document) => (
              <div className="queue-item" key={document.id}>
                <div>
                  <strong>{document.title}</strong>
                  <span>{document.category} - {document.sourceType} - {document.freshness}</span>
                </div>
                <StatusPill status={document.status} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function QualityView({ answers, feedback, lowConfidenceAnswers }) {
  return (
    <section className="content-stack">
      <div className="metric-row">
        <MetricCard icon={MessageSquare} label="Questions asked" value={answers.length} />
        <MetricCard icon={AlertCircle} label="Needs review" value={lowConfidenceAnswers.length} />
        <MetricCard icon={ThumbsUp} label="Feedback items" value={feedback.length} />
      </div>

      <div className="quality-grid">
        <div className="review-panel">
          <div className="section-heading">
            <AlertCircle size={18} />
            <h3>Low-confidence answers</h3>
          </div>
          {lowConfidenceAnswers.length ? (
            lowConfidenceAnswers.map((answer) => (
              <div className="review-item" key={answer.id}>
                <strong>{answer.question}</strong>
                <span>{answer.answer}</span>
                <ConfidenceBadge confidence={answer.confidence} status={answer.status} compact />
              </div>
            ))
          ) : (
            <p className="empty-state">No low-confidence answers yet.</p>
          )}
        </div>

        <div className="review-panel">
          <div className="section-heading">
            <ThumbsDown size={18} />
            <h3>User feedback</h3>
          </div>
          {feedback.length ? (
            feedback.map((item) => (
              <div className="review-item" key={item.id}>
                <strong>{item.feedbackType}</strong>
                <span>{item.question}</span>
                <StatusPill status={item.rating === "positive" ? "Helpful" : "Review"} />
              </div>
            ))
          ) : (
            <p className="empty-state">Feedback appears here after users rate an answer.</p>
          )}
        </div>
      </div>
    </section>
  );
}

function CitationList({ citations }) {
  if (!citations.length) {
    return (
      <div className="no-citations">
        <AlertCircle size={18} />
        <span>No citation attached. Routed to human review.</span>
      </div>
    );
  }

  return (
    <div className="citation-list">
      <div className="section-heading">
        <Link size={18} />
        <h3>Citations</h3>
      </div>
      {citations.map((citation) => (
        <a
          className="citation-card"
          href={citation.sourceUrl?.startsWith("http") ? citation.sourceUrl : undefined}
          key={`${citation.documentId}-${citation.section}-${citation.page}`}
          target="_blank"
          rel="noreferrer"
        >
          <div>
            <strong>{citation.title}</strong>
            <span>{citation.category} - {citation.section} - page {citation.page}</span>
          </div>
          <ChevronRight size={18} />
        </a>
      ))}
    </div>
  );
}

function DocumentCard({ document }) {
  return (
    <article className="document-card">
      <div className="document-topline">
        <span>{document.category}</span>
        <StatusPill status={document.status} />
      </div>
      <h3>{document.title}</h3>
      <p>{document.summary}</p>
      <div className="document-meta">
        <span>{document.language}</span>
        <span>{document.sourceType}</span>
        <span>{document.freshness}</span>
      </div>
      <a
        href={document.sourceUrl?.startsWith("http") ? document.sourceUrl : undefined}
        target="_blank"
        rel="noreferrer"
      >
        <Link size={16} />
        Source
      </a>
    </article>
  );
}

function MetricCard({ icon: Icon, label, value }) {
  return (
    <div className="metric-card">
      <Icon size={20} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ConfidenceBadge({ confidence, status, compact = false }) {
  const percent = Math.round(confidence * 100);
  const className = confidence >= 0.74 ? "confidence high" : confidence >= 0.58 ? "confidence medium" : "confidence low";

  return (
    <span className={className} title={`${percent}% confidence`}>
      {compact ? `${percent}%` : `${status} - ${percent}%`}
    </span>
  );
}

function StatusPill({ status }) {
  const normalized = status.toLowerCase().replace(/\s+/g, "-");
  return <span className={`status-pill ${normalized}`}>{status}</span>;
}

export default App;
