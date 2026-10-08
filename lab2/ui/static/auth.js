// Экран входа и регистрации. После регистрации пользователь входит сразу (тот же email и пароль).

import { api, session } from "./api.js";

const MODES = {
  login: {
    title: "Вход", submit: "Войти", switchText: "Нет аккаунта?", switchButton: "Зарегистрироваться",
    autocomplete: "current-password",
  },
  register: {
    title: "Регистрация", submit: "Зарегистрироваться", switchText: "Уже есть аккаунт?", switchButton: "Войти",
    autocomplete: "new-password",
  },
};
const PASSWORD_MIN_LENGTH = 8; // как PASSWORD_MIN_LENGTH auth-service; сервер проверяет сам (weak_password)

export function initAuth({ onAuthenticated }) {
  const view = document.getElementById("auth-view");
  const form = document.getElementById("auth-form");
  const email = document.getElementById("auth-email");
  const password = document.getElementById("auth-password");
  const submit = document.getElementById("auth-submit");
  const error = document.getElementById("auth-error");
  const notice = document.getElementById("auth-notice");
  let mode = "login";

  function setMode(next) {
    mode = next;
    const text = MODES[mode];
    document.getElementById("auth-title").textContent = text.title;
    submit.textContent = text.submit;
    document.getElementById("auth-switch-text").textContent = text.switchText;
    document.getElementById("auth-switch").textContent = text.switchButton;
    document.getElementById("auth-password-hint").hidden = mode !== "register";
    password.autocomplete = text.autocomplete;
    showError(null);
  }

  function showError(message) {
    error.textContent = message ?? "";
    error.hidden = !message;
  }

  function validate() {
    if (!email.value.trim() || !email.validity.valid) return "Введите корректный email";
    if (!password.value) return "Введите пароль";
    if (mode === "register" && password.value.length < PASSWORD_MIN_LENGTH) {
      return `Пароль должен быть не короче ${PASSWORD_MIN_LENGTH} символов`;
    }
    return null;
  }

  document.getElementById("auth-switch").addEventListener("click", () => setMode(mode === "login" ? "register" : "login"));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const problem = validate();
    if (problem) return showError(problem);

    const credentials = { email: email.value.trim(), password: password.value };
    submit.disabled = true;
    showError(null);
    try {
      if (mode === "register") await api("POST", "/api/auth/register", credentials);
      const { access_token: token } = await api("POST", "/api/auth/login", credentials);
      session.save(token);
      const user = await api("GET", "/api/auth/me");
      form.reset();
      notice.hidden = true;
      onAuthenticated(user);
    } catch (failure) {
      session.clear();
      showError(failure.message);
    } finally {
      submit.disabled = false;
    }
  });

  return {
    /** Показать экран входа; message — пояснение, например «сессия истекла». */
    show(message = null) {
      setMode("login");
      notice.textContent = message ?? "";
      notice.hidden = !message;
      view.hidden = false;
      email.focus();
    },
    hide() {
      view.hidden = true;
    },
  };
}
