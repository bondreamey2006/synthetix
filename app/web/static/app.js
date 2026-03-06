const askBtn = document.getElementById("askBtn");
const uploadBtn = document.getElementById("uploadBtn");
const themeToggle = document.getElementById("themeToggle");
const refreshDocsBtn = document.getElementById("refreshDocsBtn");
const selectAllDocsBtn = document.getElementById("selectAllDocsBtn");
const unselectAllDocsBtn = document.getElementById("unselectAllDocsBtn");
const deleteSelectedBtn = document.getElementById("deleteSelectedBtn");
const clearAllBtn = document.getElementById("clearAllBtn");
const filesEl = document.getElementById("files");
const questionEl = document.getElementById("question");
const statusEl = document.getElementById("status");
const uploadStatusEl = document.getElementById("uploadStatus");
const docsStatusEl = document.getElementById("docsStatus");
const uploadMetaEl = document.getElementById("uploadMeta");
const docsListEl = document.getElementById("docsList");
const answerEl = document.getElementById("answerText");
const sourcesEl = document.getElementById("sources");
const confidenceBadge = document.getElementById("confidenceBadge");
const overallScoreEl = document.getElementById("overallScore");
const workspaceInfoEl = document.getElementById("workspaceInfo");

function applyTheme(theme) {
  document.body.setAttribute("data-theme", theme);
  themeToggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
  localStorage.setItem("ui-theme", theme);
}

function initializeTheme() {
  const savedTheme = localStorage.getItem("ui-theme");
  if (savedTheme === "dark" || savedTheme === "light") {
    applyTheme(savedTheme);
    return;
  }
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(prefersDark ? "dark" : "light");
}

function setStatus(text) {
  statusEl.textContent = text;
}

function setUploadStatus(text) {
  uploadStatusEl.textContent = text;
}

function setDocsStatus(text) {
  docsStatusEl.textContent = text;
}

function setConfidence(confidence) {
  confidenceBadge.textContent = confidence ? confidence.toUpperCase() : "-";
  confidenceBadge.className = "badge";
  if (confidence) {
    confidenceBadge.classList.add(confidence.toLowerCase());
  }
}

function setUploadMeta(text) {
  uploadMetaEl.textContent = text;
}

function setOverallScore(score) {
  if (typeof score !== "number" || Number.isNaN(score)) {
    overallScoreEl.textContent = "Score: -";
    return;
  }
  overallScoreEl.textContent = `Score: ${(score * 100).toFixed(2)}%`;
}

function clearSources() {
  sourcesEl.replaceChildren();
}

function renderSources(sources) {
  clearSources();
  if (!Array.isArray(sources) || sources.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "No citations available for this response.";
    sourcesEl.appendChild(empty);
    return;
  }

  sources.forEach((source) => {
    const card = document.createElement("article");
    card.className = "source";

    const meta = document.createElement("div");
    meta.className = "source-meta";
    const score = typeof source.score === "number" ? `${(source.score * 100).toFixed(2)}%` : source.score;
    meta.textContent = `${source.document} | score: ${score}`;

    const snippet = document.createElement("p");
    snippet.className = "source-snippet";
    snippet.textContent = source.snippet;

    card.appendChild(meta);
    card.appendChild(snippet);
    sourcesEl.appendChild(card);
  });
}

function selectedDocNames() {
  const selected = [];
  const checkboxes = docsListEl.querySelectorAll('input[type="checkbox"]:checked');
  checkboxes.forEach((box) => {
    selected.push(box.value);
  });
  return selected;
}

function renderDocs(files) {
  docsListEl.replaceChildren();
  if (!Array.isArray(files) || files.length === 0) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No uploaded documents yet.";
    docsListEl.appendChild(empty);
    return;
  }

  files.forEach((name) => {
    const row = document.createElement("div");
    row.className = "doc-item";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = name;
    checkbox.id = `doc-${name}`;

    const label = document.createElement("label");
    label.setAttribute("for", checkbox.id);
    label.textContent = name;

    row.appendChild(checkbox);
    row.appendChild(label);
    docsListEl.appendChild(row);
  });
}

async function parseError(response, fallbackMessage) {
  try {
    const data = await response.json();
    if (data && typeof data.detail === "string" && data.detail.trim()) {
      return data.detail;
    }
  } catch (_error) {
    // ignore parse errors
  }
  return fallbackMessage;
}

async function refreshDocuments() {
  setDocsStatus("Loading files...");
  try {
    const response = await fetch("/documents");
    if (!response.ok) {
      throw new Error(await parseError(response, "Unable to fetch documents."));
    }
    const data = await response.json();
    renderDocs(data.files || []);
    setDocsStatus(`File list updated (${(data.files || []).length} file(s)).`);
  } catch (error) {
    setDocsStatus(error.message || "Failed to load document list.");
  }
}

async function loadWorkspaceInfo() {
  try {
    const response = await fetch("/session");
    if (!response.ok) {
      workspaceInfoEl.textContent = "Workspace: unavailable";
      return;
    }
    const data = await response.json();
    const workspace = (data.user_id || "").slice(0, 8) || "unknown";
    workspaceInfoEl.textContent = `Workspace: ${workspace}`;
  } catch (_error) {
    workspaceInfoEl.textContent = "Workspace: unavailable";
  }
}

async function ask() {
  const question = questionEl.value.trim();
  if (!question) {
    setStatus("Please enter a question.");
    return;
  }

  askBtn.disabled = true;
  setStatus("Analyzing document evidence...");
  setConfidence("");
  setOverallScore(NaN);

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(await parseError(response, "Backend request failed."));
    }

    const data = await response.json();
    answerEl.textContent = data.answer || "No answer returned.";
    setConfidence(data.confidence || "low");
    setOverallScore(data.score);
    renderSources(data.sources || []);
    setStatus("Done.");
  } catch (_error) {
    answerEl.textContent = "Unable to process request right now.";
    renderSources([]);
    setConfidence("low");
    setOverallScore(0);
    setStatus("Request failed.");
  } finally {
    askBtn.disabled = false;
  }
}

async function uploadDocuments() {
  const files = filesEl.files;
  if (!files || files.length === 0) {
    setUploadStatus("Please choose at least one file.");
    return;
  }

  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  uploadBtn.disabled = true;
  askBtn.disabled = true;
  setUploadStatus("Uploading and indexing...");
  setUploadMeta("");

  try {
    const response = await fetch("/upload-documents", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(await parseError(response, "Upload failed."));
    }

    const data = await response.json();
    setUploadStatus("Upload complete.");
    setUploadMeta(
      `Saved ${data.saved_files.length} file(s). Indexed ${data.ingested_documents} documents into ${data.generated_chunks} chunks.`
    );
    await refreshDocuments();
  } catch (error) {
    setUploadStatus(error.message || "Unable to upload files.");
  } finally {
    uploadBtn.disabled = false;
    askBtn.disabled = false;
  }
}

async function deleteSelectedDocuments() {
  const filenames = selectedDocNames();
  if (filenames.length === 0) {
    setDocsStatus("Select at least one file to delete.");
    return;
  }

  setDocsStatus("Deleting selected files...");
  deleteSelectedBtn.disabled = true;
  try {
    const response = await fetch("/documents/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filenames }),
    });
    if (!response.ok) {
      throw new Error(await parseError(response, "Delete failed."));
    }
    const data = await response.json();
    renderDocs(data.remaining_files || []);
    setDocsStatus(`Deleted ${data.deleted_files.length} file(s).`);
  } catch (error) {
    setDocsStatus(error.message || "Failed to delete selected files.");
  } finally {
    deleteSelectedBtn.disabled = false;
  }
}

async function clearAllDocuments() {
  const confirmed = window.confirm("Delete all uploaded documents and clear the index?");
  if (!confirmed) {
    return;
  }

  setDocsStatus("Clearing all documents...");
  clearAllBtn.disabled = true;
  try {
    const response = await fetch("/documents/clear", { method: "POST" });
    if (!response.ok) {
      throw new Error(await parseError(response, "Clear failed."));
    }
    const data = await response.json();
    renderDocs(data.remaining_files || []);
    setDocsStatus(`All documents cleared (${data.deleted_files.length} removed).`);
  } catch (error) {
    setDocsStatus(error.message || "Failed to clear documents.");
  } finally {
    clearAllBtn.disabled = false;
  }
}

function selectAllDocuments(checked) {
  const checkboxes = docsListEl.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((box) => {
    box.checked = checked;
  });
}

askBtn.addEventListener("click", ask);
uploadBtn.addEventListener("click", uploadDocuments);
refreshDocsBtn.addEventListener("click", refreshDocuments);
selectAllDocsBtn.addEventListener("click", () => selectAllDocuments(true));
unselectAllDocsBtn.addEventListener("click", () => selectAllDocuments(false));
deleteSelectedBtn.addEventListener("click", deleteSelectedDocuments);
clearAllBtn.addEventListener("click", clearAllDocuments);
themeToggle.addEventListener("click", () => {
  const current = document.body.getAttribute("data-theme") || "dark";
  applyTheme(current === "dark" ? "light" : "dark");
});
questionEl.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    ask();
  }
});

initializeTheme();
loadWorkspaceInfo();
refreshDocuments();
