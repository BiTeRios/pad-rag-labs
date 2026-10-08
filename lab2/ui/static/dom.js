// Мелкие помощники DOM. Текст всегда через textContent: данные сервера не интерпретируются как HTML.

export function el(tag, className = null, text = null) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== null) node.textContent = text;
  return node;
}

export function button(className, text, onClick, label = null) {
  const node = el("button", className, text);
  node.type = "button";
  if (label) node.setAttribute("aria-label", label);
  node.addEventListener("click", onClick);
  return node;
}

const DATE_TIME = new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

export function formatDate(value) {
  return value ? DATE_TIME.format(new Date(value)) : "—";
}

export function percent(rate) {
  return rate === null || rate === undefined ? "—" : `${Math.round(rate * 100)}%`;
}

/** Таблица: headers — подписи колонок, rows — массивы ячеек (строка или узел). */
export function table(headers, rows) {
  const node = el("table", "data");
  const head = node.createTHead().insertRow();
  for (const header of headers) head.append(el("th", null, header));
  const body = node.createTBody();
  for (const row of rows) {
    const tr = body.insertRow();
    for (const cell of row) {
      const td = tr.insertCell();
      td.append(cell ?? "—");
    }
  }
  return node;
}
