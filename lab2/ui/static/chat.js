// Чат: вопрос → POST /api/chat/ask → ответ со ссылками [n] на источники.
// Текст ответа вставляется только через textContent / text-узлы (без innerHTML): разметка из ответа модели
// не может выполниться как HTML. Поддержано то, что пишет LLM: абзацы, списки, `код`, **жирный**, блоки ```.

import { api } from "./api.js";
import { button, el } from "./dom.js";

const FEEDBACK_RETRIES = 3;    // ответ попадает в аналитику событием question.answered — сразу после ответа возможен 404
const SLOW_HINT_AFTER_S = 8;   // на CPU (Minikube) ответ занимает 10–20 с — предупредить, что это нормально
const INLINE = /(`[^`\n]+`)|(\*\*[^*\n]+\*\*)|(\[\d+(?:\s*,\s*\d+)*\])/g;

export function initChat({ onAnswered = () => {} } = {}) {
  const view = document.getElementById("chat-view");
  const messages = document.getElementById("messages");
  const emptyState = document.getElementById("empty-state");
  const form = document.getElementById("ask-form");
  const input = document.getElementById("question");
  const askButton = document.getElementById("ask-button");
  let conversationId = null;
  let pending = false;

  function append(node) {
    emptyState.hidden = true;
    messages.append(node);
    node.scrollIntoView({ block: "end", behavior: "smooth" });
    return node;
  }

  async function ask(question) {
    question = question.trim();
    if (pending || !question) return;
    pending = true;
    askButton.disabled = true;
    input.value = "";
    resizeInput();
    append(userBubble(question));
    const waiting = pendingBubble();
    append(waiting.node);
    let result;
    try {
      const message = await api("POST", "/api/chat/ask", { question, conversation_id: conversationId });
      conversationId = message.conversation_id;
      result = answerCard(message);
      onAnswered(conversationId);
    } catch (error) {
      if (error.status === 401) {  // токен истёк: приложение уже показало вход, вопрос вернём в поле ввода
        input.value = question;
        return;
      }
      result = errorCard(error);
    } finally {
      waiting.stop();
      pending = false;
      askButton.disabled = false;
      if (!view.hidden) input.focus();
    }
    waiting.node.replaceWith(result);
    result.scrollIntoView({ block: "nearest", behavior: "smooth" });  // длинный ответ — видно его начало
  }

  function resizeInput() {  // поле растёт с текстом до max-height из CSS, дальше — прокрутка
    input.style.height = "auto";
    input.style.height = `${input.scrollHeight}px`;
    input.style.overflowY = input.scrollHeight > input.clientHeight ? "auto" : "hidden";
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    ask(input.value);
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      ask(input.value);
    }
  });
  input.addEventListener("input", resizeInput);
  document.querySelectorAll("#examples .example").forEach((example) => {
    example.addEventListener("click", () => ask(example.textContent));
  });

  return {
    show() {
      view.hidden = false;
      input.focus();
    },
    hide() {
      view.hidden = true;
    },
    /** Очистить чат (выход, смена пользователя). */
    reset,
    /** Новый диалог по кнопке; false — идёт ответ, переключаться нельзя. */
    startNew() {
      if (pending) return false;
      reset();
      input.focus();
      return true;
    },
    /** Показать сохранённый диалог и продолжить его следующим вопросом. */
    open(conversation) {
      if (pending) return false;
      reset();
      conversationId = conversation.id;
      for (const message of conversation.messages) {
        messages.append(userBubble(message.question), answerCard(message));
      }
      emptyState.hidden = conversation.messages.length > 0;
      messages.scrollTop = messages.scrollHeight;
      input.focus();
      return true;
    },
  };

  function reset() {
    conversationId = null;
    messages.querySelectorAll(".msg").forEach((node) => node.remove());
    emptyState.hidden = false;
  }
}

function userBubble(question) {
  const row = el("div", "msg user");
  row.append(el("div", "bubble", question));
  return row;
}

function pendingBubble() {
  const row = el("div", "msg assistant");
  const card = el("div", "card pending");
  const status = el("span", "pending-text", "Ищу в документации и готовлю ответ…");
  const seconds = el("span", "pending-seconds", "0 с");
  const hint = el("p", "pending-hint", "На CPU поиск с reranker и генерация занимают 10–20 секунд.");
  hint.hidden = true;
  card.append(el("span", "spinner"), status, seconds, hint);
  row.append(card);

  const started = Date.now();
  const timer = setInterval(() => {
    const elapsed = Math.round((Date.now() - started) / 1000);
    seconds.textContent = `${elapsed} с`;
    hint.hidden = elapsed < SLOW_HINT_AFTER_S;
  }, 1000);
  return { node: row, stop: () => clearInterval(timer) };
}

function answerCard(message) {
  const row = el("div", "msg assistant");
  const card = el("article", message.refused ? "card answer refused" : "card answer");
  // Несколько фрагментов одной страницы — один источник: refs связывает с ним каждую ссылку [n] ответа
  const sourceOfRef = new Map();
  for (const source of message.sources) {
    for (const n of source.refs?.length ? source.refs : [source.n]) sourceOfRef.set(n, source);
  }
  const sourceId = (source) => `src-${message.id}-${source.n}`;

  if (message.refused) card.append(el("div", "refusal-title", "Ответа нет в документации"));
  card.append(renderMarkdown(message.answer, (n) => {
    const source = sourceOfRef.get(n);
    if (!source) return null;
    const link = el("a", "cite", String(n));
    link.href = `#${sourceId(source)}`;
    link.title = source.title;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      highlight(document.getElementById(sourceId(source)));
    });
    return link;
  }));

  if (message.sources.length) {
    card.append(el("h3", "sources-title", "Источники"));
    const list = el("ol", "sources");
    for (const source of message.sources) {
      const item = el("li");
      item.id = sourceId(source);
      const link = el("a", "source-link", source.title);
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      item.append(el("span", "source-n", String(source.n)), link);
      const section = sectionOf(source);
      if (section) item.append(el("span", "source-heading", section));
      list.append(item);
    }
    card.append(list);
  }

  const meta = [message.model ?? "без вызова LLM", `${(message.timings_ms.total / 1000).toFixed(1)} с`];
  if (message.degraded.includes("reranker")) meta.push("поиск без reranker");
  const footer = el("div", "card-footer");
  footer.append(el("div", "meta", meta.join(" · ")), ratingBar(message.id));
  card.append(footer);
  row.append(card);
  return row;
}

/** 👍/👎 под ответом → POST /api/feedback; повторная оценка заменяет прежнюю. */
function ratingBar(messageId) {
  const bar = el("div", "rating");
  const status = el("span", "rating-status");
  const choices = [[1, "👍", "Полезный ответ"], [-1, "👎", "Бесполезный ответ"]].map(([value, icon, label]) => {
    const choice = button("rate", icon, () => rate(value, choice), label);
    choice.title = label;
    choice.setAttribute("aria-pressed", "false");
    return choice;
  });

  async function rate(value, chosen) {
    choices.forEach((choice) => { choice.disabled = true; });
    status.textContent = "";
    try {
      await sendFeedback(messageId, value);
      choices.forEach((choice) => choice.setAttribute("aria-pressed", String(choice === chosen)));
      status.textContent = "Спасибо за оценку";
    } catch (failure) {
      if (failure.status !== 401) status.textContent = failure.message;
    } finally {
      choices.forEach((choice) => { choice.disabled = false; });
    }
  }

  bar.append(status, ...choices);
  return bar;
}

async function sendFeedback(messageId, rating) {
  for (let attempt = 0; ; attempt++) {
    try {
      return await api("POST", "/api/feedback", { message_id: messageId, rating });
    } catch (failure) {
      if (failure.code !== "message_unknown" || attempt === FEEDBACK_RETRIES) throw failure;
      await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
    }
  }
}

function errorCard(error) {
  const row = el("div", "msg assistant");
  const card = el("div", "card error");
  card.append(el("strong", null, error.message));
  if (error.retryAfter) card.append(el("p", null, `Повторите через ${error.retryAfter} с.`));
  if (error.requestId) card.append(el("p", "request-id", `request_id: ${error.requestId}`));
  row.append(card);
  return row;
}

/** Раздел внутри страницы: heading без повтора заголовка страницы («Pods > Lifecycle» → «Lifecycle»). */
function sectionOf(source) {
  const prefix = `${source.title} > `;
  const heading = source.heading.startsWith(prefix) ? source.heading.slice(prefix.length) : source.heading;
  return heading === source.title ? "" : heading;
}

function highlight(node) {
  if (!node) return;
  node.scrollIntoView({ block: "nearest", behavior: "smooth" });
  node.classList.remove("flash");
  void node.offsetWidth;  // перезапуск CSS-анимации при повторном клике
  node.classList.add("flash");
}

function renderMarkdown(text, cite) {
  const root = el("div", "md");
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  let paragraph = null;
  let list = null;
  let listOrdered = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim().startsWith("```")) {
      const code = [];
      while (++i < lines.length && !lines[i].trim().startsWith("```")) code.push(lines[i]);
      const pre = el("pre");
      pre.append(el("code", null, code.join("\n")));
      root.append(pre);
      paragraph = list = null;
      continue;
    }
    if (!line.trim()) {
      paragraph = list = null;
      continue;
    }
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    if (heading) {
      const node = el("p", "md-heading");
      appendInline(node, heading[1], cite);
      root.append(node);
      paragraph = list = null;
      continue;
    }
    const item = line.match(/^\s*(?:[-*•]|(\d+)[.)])\s+(.*)$/);
    if (item) {
      const ordered = item[1] !== undefined;
      if (!list || listOrdered !== ordered) {
        list = el(ordered ? "ol" : "ul");
        if (ordered && item[1] !== "1") list.start = Number(item[1]);
        listOrdered = ordered;
        root.append(list);
      }
      const li = el("li");
      appendInline(li, item[2], cite);
      list.append(li);
      paragraph = null;
      continue;
    }
    if (paragraph) {
      paragraph.append(el("br"));
    } else {
      paragraph = el("p");
      root.append(paragraph);
      list = null;
    }
    appendInline(paragraph, line, cite);
  }
  return root;
}

function appendInline(parent, text, cite) {
  let last = 0;
  for (const match of text.matchAll(INLINE)) {
    if (match.index > last) parent.append(text.slice(last, match.index));
    const [token, code, bold] = match;
    if (code) {
      parent.append(el("code", null, code.slice(1, -1)));
    } else if (bold) {
      parent.append(el("strong", null, bold.slice(2, -2)));
    } else {
      for (const n of token.slice(1, -1).split(",").map((part) => Number(part.trim()))) {
        parent.append(cite(n) ?? `[${n}]`);
      }
    }
    last = match.index + token.length;
  }
  if (last < text.length) parent.append(text.slice(last));
}
