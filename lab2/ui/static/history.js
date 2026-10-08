// Боковая панель «Диалоги»: список из chat-service, открыть, удалить (с подтверждением в строке), новый диалог.

import { api } from "./api.js";
import { button, el, formatDate } from "./dom.js";

export function initHistory({ onOpen, onNew }) {
  const workspace = document.getElementById("chat-view");
  const list = document.getElementById("conversation-list");
  const empty = document.getElementById("conversation-empty");
  const error = document.getElementById("conversation-error");
  const toggle = document.getElementById("sidebar-toggle");
  let items = [];
  let activeId = null;
  let confirmingId = null;

  function showError(message) {
    error.textContent = message ?? "";
    error.hidden = !message;
  }

  function setSidebarOpen(open) {  // на узком экране панель открывается поверх чата
    workspace.classList.toggle("sidebar-open", open);
    toggle.setAttribute("aria-expanded", String(open));
  }

  function render() {
    list.replaceChildren(...items.map(row));
    empty.hidden = items.length > 0;
  }

  function row(conversation) {
    const item = el("li", conversation.id === activeId ? "conversation active" : "conversation");
    if (conversation.id === confirmingId) {
      item.classList.add("confirming");
      item.append(
        el("span", "confirm-text", "Удалить диалог?"),
        button("danger small", "Удалить", () => remove(conversation)),
        button("ghost small", "Отмена", () => { confirmingId = null; render(); }),
      );
      return item;
    }
    const open = button("conversation-open", null, () => select(conversation.id));
    open.append(el("span", "conversation-title", conversation.title),
                el("span", "conversation-date", formatDate(conversation.updated_at)));
    if (conversation.id === activeId) open.setAttribute("aria-current", "true");
    const removeButton = button("conversation-delete", "✕", () => { confirmingId = conversation.id; render(); },
                                `Удалить диалог «${conversation.title}»`);
    removeButton.title = "Удалить диалог";
    item.append(open, removeButton);
    return item;
  }

  async function refresh() {
    try {
      items = (await api("GET", "/api/chat/conversations?limit=50")).items;
      showError(null);
      render();
    } catch (failure) {
      if (failure.status !== 401) showError(failure.message);
    }
  }

  async function select(id) {
    try {
      const conversation = await api("GET", `/api/chat/conversations/${encodeURIComponent(id)}`);
      if (onOpen(conversation) === false) return;  // чат ждёт ответа — переключаться нельзя
      activeId = id;
      confirmingId = null;
      render();
      setSidebarOpen(false);
    } catch (failure) {
      if (failure.status === 401) return;
      showError(failure.message);
      if (failure.status === 404) refresh();  // диалог удалён в другой вкладке
    }
  }

  async function remove(conversation) {
    try {
      await api("DELETE", `/api/chat/conversations/${encodeURIComponent(conversation.id)}`);
      confirmingId = null;
      if (conversation.id === activeId) {
        activeId = null;
        onNew();
      }
      await refresh();
    } catch (failure) {
      if (failure.status !== 401) showError(failure.message);
    }
  }

  document.getElementById("new-conversation").addEventListener("click", () => {
    if (onNew() === false) return;
    activeId = null;
    render();
    setSidebarOpen(false);
  });
  toggle.addEventListener("click", () => setSidebarOpen(!workspace.classList.contains("sidebar-open")));

  return {
    refresh,
    /** Диалог стал текущим после ответа (новый диалог создаётся первым вопросом). */
    setActive(id) {
      activeId = id;
      render();
    },
    clear() {
      items = [];
      activeId = confirmingId = null;
      showError(null);
      render();
      setSidebarOpen(false);
    },
  };
}
