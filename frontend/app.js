const state = {
  sessionId: null,
  mode: "url", // "url" | "file"
};

// ---- Tabs ----
const tabs = document.querySelectorAll(".tab");
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });
    tab.classList.add("active");
    tab.setAttribute("aria-selected", "true");

    state.mode = tab.dataset.tab;
    document.getElementById("tab-url").classList.toggle("hidden", state.mode !== "url");
    document.getElementById("tab-file").classList.toggle("hidden", state.mode !== "file");
  });
});

// ---- File name preview ----
const fileInput = document.getElementById("file-input");
const fileNameLabel = document.getElementById("file-name");
fileInput.addEventListener("change", () => {
  fileNameLabel.textContent = fileInput.files.length
    ? `Selected: ${fileInput.files[0].name}`
    : "";
});

// ---- Process button ----
const processBtn = document.getElementById("process-btn");
const statusLine = document.getElementById("status-line");
const resultsSection = document.getElementById("results");
const chatPanel = document.getElementById("chat-panel");

function setStatus(text, isError = false) {
  statusLine.textContent = text;
  statusLine.classList.toggle("error", isError);
}

processBtn.addEventListener("click", async () => {
  const formData = new FormData();

  if (state.mode === "url") {
    const url = document.getElementById("youtube-url").value.trim();
    if (!url) {
      setStatus("Paste a YouTube URL first.", true);
      return;
    }
    formData.append("youtube_url", url);
  } else {
    const file = fileInput.files[0];
    if (!file) {
      setStatus("Choose a file first.", true);
      return;
    }
    formData.append("file", file);
  }

  processBtn.disabled = true;
  setStatus("Processing — this can take a few minutes for longer recordings...");
  resultsSection.classList.add("hidden");
  chatPanel.classList.add("hidden");

  try {
    const res = await fetch("/api/process", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }

    const data = await res.json();
    state.sessionId = data.session_id;
    renderResults(data);
    setStatus("Done.");
    resultsSection.classList.remove("hidden");
    chatPanel.classList.remove("hidden");
  } catch (e) {
    setStatus(e.message || "Something went wrong.", true);
  } finally {
    processBtn.disabled = false;
  }
});

function renderResults(data) {
  document.getElementById("result-title").textContent = data.title;
  document.getElementById("result-summary").textContent = data.summary;
  document.getElementById("result-actions").textContent = data.action_items;
  document.getElementById("result-decisions").textContent = data.key_decisions;
  document.getElementById("result-questions").textContent = data.open_questions;
}

// ---- Chat ----
const chatLog = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

function appendMessage(text, role) {
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendChat() {
  const question = chatInput.value.trim();
  if (!question || !state.sessionId) return;

  appendMessage(question, "user");
  chatInput.value = "";
  chatSend.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: state.sessionId, question }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Couldn't get an answer.");
    }

    const data = await res.json();
    appendMessage(data.answer, "assistant");
  } catch (e) {
    appendMessage(e.message || "Something went wrong.", "assistant");
  } finally {
    chatSend.disabled = false;
  }
}

chatSend.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChat();
});