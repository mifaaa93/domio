(function () {
  const tg = window.Telegram?.WebApp;
  if (tg) tg.expand();

  // читаем параметры
  const qs = new URLSearchParams(location.search);
  const lang = (qs.get("lang") || "uk").toLowerCase();

  // простая локализация
  const T = {
    preparing: { uk: "Готуємо оплату…", pl: "Przygotowujemy płatność…", en: "Preparing payment…" },
    creating:  { uk: "Створюємо рахунок…", pl: "Tworzymy fakturę…",       en: "Creating invoice…" },
    opening:   { uk: "Відкриваємо оплату…", pl: "Otwieramy płatność…",     en: "Opening payment…" },
    failed:    { uk: "Не вдалося створити рахунок. Спробуйте пізніше.",
                 pl: "Nie udało się utworzyć rachunku. Spróbuj ponownie później.",
                 en: "Failed to create invoice. Please try again later." }
  };
  const L = (key) => (T[key]?.[lang] || T[key]?.uk || "");
  // Превращаем QueryString в объект
  const qsPayload = Object.fromEntries(qs.entries());
  const msg = document.getElementById("msg");
  const API_BASE = "/api";

  function getInitData() { return tg?.initData || ""; }

  async function go() {
    try {
      msg.textContent = L("creating");

      // IP больше НЕ шлём — бек его сам определяет
      const initData = getInitData();

      const r = await fetch(`${API_BASE}/invoices/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Init-Data": initData,
        },
        body: JSON.stringify(qsPayload)
      });

      if (!r.ok) throw new Error(await r.text().catch(() => "HTTP error"));

      const j = await r.json();
      const url = j.redirectUri;
      if (!url) throw new Error("No redirectUri");

      msg.textContent = L("opening");
      if (tg?.openLink) tg.openLink(url); else window.location.href = url;
      setTimeout(() => { try { tg?.close(); } catch(e){} }, 400);

    } catch (e) {
      console.error(e);
      msg.textContent = L("failed");
    }
  }

  // стартовый текст (до начала запроса)
  msg.textContent = L("preparing");
  go();
})();
