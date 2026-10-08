// Точка входа: при наличии токена — сразу чат (токен проверяется через /api/auth/me), иначе экран входа.
// Вкладка «Администрирование» показывается только роли admin.

import { api, session, setUnauthorizedHandler } from "./api.js";
import { initAdmin } from "./admin.js";
import { initAuth } from "./auth.js";
import { initChat } from "./chat.js";
import { initHistory } from "./history.js";

const userBox = document.getElementById("user-box");
const tabs = document.getElementById("tabs");
const chat = initChat({
  onAnswered(conversationId) {  // новый диалог создаётся первым вопросом — обновить список и выделить его
    history.setActive(conversationId);
    history.refresh();
  },
});
const history = initHistory({ onOpen: (conversation) => chat.open(conversation), onNew: () => chat.startNew() });
const admin = initAdmin();
const auth = initAuth({ onAuthenticated: showWorkspace });

function switchView(name) {
  tabs.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.view === name));
  if (name === "admin") {
    chat.hide();
    admin.show();
  } else {
    admin.hide();
    chat.show();
  }
}

function showWorkspace(user) {
  document.getElementById("user-email").textContent = user.email;
  const role = document.getElementById("user-role");
  role.textContent = user.role;
  role.classList.toggle("is-admin", user.role === "admin");
  userBox.hidden = false;
  tabs.hidden = user.role !== "admin";
  auth.hide();
  switchView("chat");
  history.refresh();
}

function showAuth(message = null) {
  userBox.hidden = true;
  tabs.hidden = true;
  chat.hide();
  chat.reset();
  history.clear();
  admin.hide();
  auth.show(message);
}

tabs.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => switchView(tab.dataset.view)));

document.getElementById("logout").addEventListener("click", () => {
  session.clear();
  showAuth();
});

setUnauthorizedHandler(() => {
  session.clear();
  showAuth("Сессия истекла — войдите снова");
});

async function start() {
  if (!session.token) return showAuth();
  try {
    showWorkspace(await api("GET", "/api/auth/me"));
  } catch (error) {
    if (error.status !== 401) showAuth(error.message);  // 401 уже обработан: показан вход
  }
}

start();
