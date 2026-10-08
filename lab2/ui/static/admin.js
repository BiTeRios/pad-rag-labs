// Панель администратора: готовность сервисов, индекс, синхронизация корпуса, аналитика.
// Видна только роли admin; сервисы проверяют роль сами, поэтому 403 здесь показывается как обычная ошибка.

import { api } from "./api.js";
import { el, formatDate, percent, table } from "./dom.js";

const POLL_MS = 3000;   // пока идёт синхронизация или индексация, панель обновляется сама
const SERVICE_STATE = { ready: ["готов", "ok"], not_ready: ["не готов", "warn"], unreachable: ["недоступен", "bad"] };
const RUN_STATE = { running: ["идёт", "warn"], succeeded: ["успешно", "ok"], partial: ["частично", "warn"], failed: ["ошибка", "bad"] };

export function initAdmin() {
  const view = document.getElementById("admin-view");
  const boxes = {
    status: document.getElementById("admin-status"),
    index: document.getElementById("admin-index"),
    runs: document.getElementById("admin-runs"),
    summary: document.getElementById("admin-summary"),
  };
  const syncButton = document.getElementById("sync-start");
  const syncError = document.getElementById("sync-error");
  let timer = null;

  async function section(box, request, render) {
    try {
      const data = await request();
      box.replaceChildren(render(data));
      return data;
    } catch (failure) {
      if (failure.status === 503 && failure.data?.services) {  // /api/status: часть сервисов не готова
        box.replaceChildren(render(failure.data));
        return failure.data;
      }
      if (failure.status !== 401) box.replaceChildren(el("p", "form-error", failure.message));
      return null;
    }
  }

  async function load() {
    clearTimeout(timer);
    const [, index, runs] = await Promise.all([
      section(boxes.status, () => api("GET", "/api/status"), renderStatus),
      section(boxes.index, () => api("GET", "/api/indexing/status"), renderIndex),
      section(boxes.runs, () => api("GET", "/api/ingestion/runs"), renderRuns),
      section(boxes.summary, () => api("GET", "/api/analytics/summary"), renderSummary),
    ]);
    const busy = Boolean(index?.running) || Boolean(runs?.some((run) => run.status === "running"));
    syncButton.disabled = Boolean(runs?.some((run) => run.status === "running"));
    if (busy && !view.hidden) timer = setTimeout(load, POLL_MS);
  }

  syncButton.addEventListener("click", async () => {
    syncError.hidden = true;
    syncButton.disabled = true;
    try {
      await api("POST", "/api/ingestion/runs");
    } catch (failure) {
      if (failure.status !== 401) {
        syncError.textContent = failure.code === "sync_running" ? "Синхронизация уже идёт" : failure.message;
        syncError.hidden = false;
      }
    }
    await load();
  });
  document.getElementById("admin-refresh").addEventListener("click", load);

  return {
    show() {
      view.hidden = false;
      load();
    },
    hide() {
      view.hidden = true;
      clearTimeout(timer);
    },
  };
}

function state(map, value) {
  const [text, tone] = map[value] ?? [value, "warn"];
  return el("span", `state ${tone}`, text);
}

function renderStatus(data) {
  const box = el("div");
  box.append(el("p", "panel-note", data.status === "ok" ? "Все сервисы готовы" : "Часть сервисов не готова"));
  box.append(table(["Сервис", "Состояние (/ready)"],
                   Object.entries(data.services).map(([name, value]) => [name, state(SERVICE_STATE, value)])));
  return box;
}

function renderIndex(data) {
  const chunking = data.chunking ?? {};
  const job = data.last_job;
  const rows = [
    ["Коллекция", data.collection],
    ["Модель эмбеддингов", data.embedding_model],
    ["Chunking", `${chunking.strategy}, ${chunking.chunk_size} символов, overlap ${chunking.chunk_overlap}`],
    ["Документов / chunks", `${data.documents ?? "—"} / ${data.points ?? "—"}`],
    ["Сейчас", data.running ? `идёт индексация (${data.running.trigger}) с ${formatDate(data.running.started_at)}` : "простаивает"],
  ];
  if (job) {
    const stats = job.stats ?? {};
    rows.push(["Последняя задача", `${job.trigger}, ${job.status}, ${job.duration_s} с, ${formatDate(job.started_at)}`],
              ["Изменения", `добавлено ${stats.added ?? 0}, обновлено ${stats.updated ?? 0}, удалено ${stats.deleted ?? 0}, chunks ${stats.chunks_indexed ?? 0}`]);
  }
  return definitions(rows);
}

function renderRuns(runs) {
  if (!runs.length) return el("p", "panel-note", "Синхронизаций ещё не было");
  return table(["Начало", "Запуск", "Статус", "Добавлено", "Обновлено", "Без изменений", "Удалено", "Ошибок", "Длительность"],
    runs.slice(0, 5).map((run) => [
      formatDate(run.started_at), run.trigger, state(RUN_STATE, run.status), String(run.added), String(run.updated),
      String(run.unchanged), String(run.deleted), String(run.failed), duration(run.started_at, run.finished_at),
    ]));
}

function renderSummary(data) {
  const box = el("div");
  const tiles = el("div", "tiles");
  const feedback = data.feedback ?? {};
  for (const [label, value] of [
    ["Вопросов", String(data.questions)],
    ["Доля отказов", percent(data.refusal_rate)],
    ["Ответ: среднее / p95", data.latency_ms?.mean ? `${seconds(data.latency_ms.mean)} / ${seconds(data.latency_ms.p95)}` : "—"],
    ["Оценки 👍 / 👎", `${feedback.positive ?? 0} / ${feedback.negative ?? 0}`],
    ["Поиск без reranker", percent(data.degraded_rate)],
    ["Пользователей", String(data.users_registered)],
  ]) {
    const tile = el("div", "tile");
    tile.append(el("span", "tile-value", value), el("span", "tile-label", label));
    tiles.append(tile);
  }
  box.append(tiles);
  if (data.top_sources?.length) {
    box.append(el("h3", "panel-subtitle", "Чаще всего цитируемые документы"));
    box.append(table(["Документ", "Ссылок"], data.top_sources.slice(0, 5).map((s) => [s.document_id, String(s.citations)])));
  }
  return box;
}

function definitions(rows) {
  const list = el("dl", "definitions");
  for (const [term, value] of rows) list.append(el("dt", null, term), el("dd", null, value ?? "—"));
  return list;
}

function seconds(ms) {
  return ms === null || ms === undefined ? "—" : `${(ms / 1000).toFixed(1)} с`;
}

function duration(start, finish) {
  return finish ? `${Math.max(0, Math.round((new Date(finish) - new Date(start)) / 1000))} с` : "—";
}
