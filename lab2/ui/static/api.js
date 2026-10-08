// HTTP-клиент gateway: тот же origin (nginx проксирует /api), JWT из sessionStorage, единый формат ошибок
// {"error": {"code", "message", "request_id"}} → ApiError.

const TOKEN_KEY = "rag.token";

const DEFAULT_MESSAGES = {
  0: "Сервер недоступен — проверьте подключение",
  429: "Слишком много запросов — подождите немного",
  502: "Сервис временно недоступен",
  503: "Сервис временно недоступен",
  504: "Сервис не ответил вовремя — попробуйте ещё раз",
};

export class ApiError extends Error {
  constructor(status, code, message, requestId = null, retryAfter = null, data = null) {
    super(message);
    this.status = status;
    this.code = code;
    this.requestId = requestId;
    this.retryAfter = retryAfter;
    this.data = data;  // тело ответа: /api/status при 503 отдаёт состояние сервисов, а не error
  }
}

// sessionStorage: токен живёт до закрытия вкладки; в приватном режиме хранилище может быть недоступно
export const session = {
  get token() {
    try { return sessionStorage.getItem(TOKEN_KEY); } catch { return null; }
  },
  save(token) {
    try { sessionStorage.setItem(TOKEN_KEY, token); } catch { /* без хранилища — до перезагрузки страницы */ }
    memoryToken = token;
  },
  clear() {
    try { sessionStorage.removeItem(TOKEN_KEY); } catch { /* нечего чистить */ }
    memoryToken = null;
  },
};
let memoryToken = null;

let onUnauthorized = () => {};

/** Вызывается, когда gateway отверг выданный ранее токен (истёк или подпись неверна). */
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

export async function api(method, path, body) {
  const token = session.token ?? memoryToken;
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, "network_error", DEFAULT_MESSAGES[0]);
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (response.ok) return data;

  const error = data?.error ?? {};
  const apiError = new ApiError(
    response.status,
    error.code ?? `http_${response.status}`,
    error.message ?? DEFAULT_MESSAGES[response.status] ?? `Ошибка ${response.status}`,
    error.request_id ?? response.headers.get("X-Request-ID"),
    response.headers.get("Retry-After"),
    data,
  );
  if (response.status === 401 && token) onUnauthorized(apiError);
  throw apiError;
}
