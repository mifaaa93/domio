(function () {
  const $ = (sel) => document.querySelector(sel);
  const tg = window.Telegram?.WebApp;

  // Без Telegram WebApp смысла нет — подскажем пользователю
  if (!tg) {
    showError("Откройте страницу через Telegram мини-апп.");
    return;
  }

  // Инициализация Telegram WebApp UI
  tg.ready();
  if (typeof tg.expand === "function") tg.expand();
  // Реакция на смену темы (по желанию)
  if (typeof tg.onEvent === "function") {
    tg.onEvent("themeChanged", () => {
      document.documentElement.dataset.theme = tg.colorScheme || "light";
    });
  }

  // Чтение параметров URL
  const params = new URLSearchParams(location.search);
  const searchId = params.get("search_id");
  $("#searchId").textContent = searchId ?? "—";

  // Сырой initData — НЕЛЬЗЯ парсить/менять!
  const initData = tg.initData;

  // Кнопки
  $("#refreshBtn").addEventListener("click", () => location.reload());

  // Запрос к вашему бэку
  fetch(`${window.BACKEND_URL}/api/listings/count`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      "X-Telegram-Init-Data": initData
    },
    cache: "no-store"
    // credentials: "include", // включите при необходимости кук
    // mode: "cors"           // если бэк на другом домене
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      return res.json();
    })
    .then((json) => {
      $("#total").textContent = json?.total ?? 0;
    })
    .catch((err) => {
      showError(err?.message || "Ошибка запроса");
    });

  function showError(msg) {
    const el = $("#error");
    el.textContent = msg;
    el.hidden = false;
  }
})();
