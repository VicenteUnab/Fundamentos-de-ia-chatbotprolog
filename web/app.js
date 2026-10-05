"use strict";

const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question");
const modelSelect = document.querySelector("#model");
const messages = document.querySelector("#messages");
const sendButton = document.querySelector("#send-button");
const clearButton = document.querySelector("#clear-chat");
const statusText = document.querySelector("#status");
const suggestionButtons = document.querySelectorAll(".suggestion");

let sending = false;

function scrollToLatest() {
  messages.scrollTop = messages.scrollHeight;
}

function addMessage(text, role, author) {
  const article = document.createElement("article");
  article.classList.add("message", role);

  if (role !== "user") {
    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = role === "error" ? "!" : "🌿";
    article.appendChild(avatar);
  }

  const content = document.createElement("div");
  content.className = "message-content";

  const authorLabel = document.createElement("span");
  authorLabel.className = "message-author";
  authorLabel.textContent = author;

  const paragraph = document.createElement("p");
  paragraph.textContent = text;

  content.append(authorLabel, paragraph);
  article.appendChild(content);
  messages.appendChild(article);

  scrollToLatest();
}

function setSending(value) {
  sending = value;
  sendButton.disabled = value;
  modelSelect.disabled = value;
  clearButton.disabled = value;

  suggestionButtons.forEach((button) => {
    button.disabled = value;
  });

  sendButton.textContent = value ? "Enviando…" : "Enviar ↗";
  messages.setAttribute("aria-busy", String(value));
}

async function sendQuestion() {
  if (sending) return;

  const question = questionInput.value.trim();

  if (!question) {
    statusText.textContent = "Escribe una pregunta para continuar.";
    questionInput.focus();
    return;
  }

  if (question.length > 1000) {
    statusText.textContent = "La pregunta debe tener como máximo 1000 caracteres.";
    return;
  }

  const model = modelSelect.value;
  const modelName = model === "prolog" ? "Prolog" : "Gemini";

  addMessage(question, "user", "Tú");
  questionInput.value = "";
  setSending(true);
  statusText.textContent = `${modelName} está preparando la respuesta…`;

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 90000);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pregunta: question,
        modelo: model,
      }),
      signal: controller.signal,
    });

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error("El servidor no devolvió una respuesta válida.");
    }

    if (!response.ok) {
      throw new Error(data.error || "No se pudo obtener la respuesta.");
    }

    if (typeof data.respuesta !== "string" || !data.respuesta.trim()) {
      throw new Error("El servidor devolvió una respuesta vacía.");
    }

    addMessage(data.respuesta, "bot", `Botánica · ${modelName}`);
    statusText.textContent = "";
  } catch (error) {
    let message;

    if (error.name === "AbortError") {
      message = "La respuesta tardó demasiado. Intenta nuevamente.";
    } else if (error instanceof TypeError) {
      message = "No pude conectar con el servidor. Comprueba que siga ejecutándose.";
    } else {
      message = error.message || "Ocurrió un error al enviar la pregunta.";
    }

    addMessage(message, "error", "Error de conexión o respuesta");
    statusText.textContent = "Puedes volver a intentar la consulta.";

    if (!questionInput.value) {
      questionInput.value = question;
    }
  } finally {
    window.clearTimeout(timeout);
    setSending(false);
    questionInput.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendQuestion();
});

suggestionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (sending) return;

    questionInput.value = button.dataset.question;
    sendQuestion();
  });
});

clearButton.addEventListener("click", () => {
  if (sending) return;

  messages.replaceChildren();
  statusText.textContent = "";

  addMessage(
    "¡Hola! Puedo ayudarte con las plantas de nuestra base. Pregúntame por sus cuidados o elige una sugerencia.",
    "bot",
    "Botánica"
  );

  questionInput.focus();
});