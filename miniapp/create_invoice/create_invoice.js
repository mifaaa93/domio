(function () {
  const tg = window.Telegram?.WebApp;
  if (tg) { tg.expand(); tg.ready(); }

  const qs = new URLSearchParams(location.search);
  const lang = (qs.get("lang") || "uk").toLowerCase();

  const T = {
    preparing: { uk:"Готуємо оплату…", pl:"Przygotowujemy płatność…", en:"Preparing payment…" },
    creating:  { uk:"Створюємо рахунок…", pl:"Tworzymy fakturę…",       en:"Creating invoice…" },
    open_btn:  { uk:"Відкрити оплату у браузері", pl:"Otwórz płatność w przeglądarce", en:"Open payment in browser" },
    link_ready:   { uk: "Посилання на оплату готове", pl: "Link do płatności jest gotowy", en: "Payment link is ready" },
    failed:    { uk:"Не вдалося створити рахунок. Спробуйте пізніше.",
                 pl:"Nie udało się utworzyć rachunku. Spróbuj ponownie później.",
                 en:"Failed to create invoice. Please try again later." },
    copy_hint: { uk:"Якщо браузер не відкрився — натисніть і утримуйте кнопку, щоб скопіювати посилання.",
                 pl:"Jeśli przeglądarka się nie otworzyła — przytrzymaj przycisk, aby skopiować link.",
                 en:"If the browser didn’t open, long-press the button to copy the link." }
  };
  const L = (k) => (T[k]?.[lang] || T[k]?.uk || "");

  const msg = document.getElementById("msg");
  const btn = document.getElementById("payBtn");
  const hint = document.getElementById("copyHint");
  const API_BASE = "/api";
  const qsPayload = Object.fromEntries(qs.entries());

  msg.textContent = L("preparing");

  function armButton(url) {
    btn.textContent = L("open_btn");
    btn.style.display = "inline-block";
    hint.textContent = L("copy_hint");
    hint.style.display = "block";

    btn.onclick = () => {
      try {
        if (tg?.openLink) {
          tg.openLink(url, { try_browser: true }); // внешний браузер
        } else {
          const a = document.createElement("a");
          a.href = url; a.target = "_blank"; a.rel = "noopener";
          document.body.appendChild(a); a.click();
          setTimeout(() => { window.location.assign(url); }, 0);
        }
        setTimeout(() => { try { tg?.close(); } catch(_){} }, 1500);
      } catch (e) { console.error(e); }
    };

    // Долгое нажатие — скопировать ссылку
    btn.oncontextmenu = async (ev) => {
      ev.preventDefault();
      try {
        await navigator.clipboard.writeText(url);
        const old = btn.textContent;
        btn.textContent = "✅ " + old;
        setTimeout(() => (btn.textContent = old), 1200);
      } catch {}
    };
  }

  (async function go() {
    try {
      msg.textContent = L("creating");
      const r = await fetch(`${API_BASE}/invoices/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Init-Data": tg?.initData || "",
        },
        body: JSON.stringify(qsPayload)
      });
      if (!r.ok) throw new Error(await r.text().catch(() => "HTTP error"));

      const j = await r.json();
      const url = j.redirectUri;
      if (!url) throw new Error("No redirectUri");

      msg.textContent = L("link_ready");
      // ✨ стопим лоадер/анимацию до ожидания клика
      const sp = document.querySelector('.spinner');
      if (sp) sp.style.display = 'none';
      armButton(url); // ждём явный клик пользователя
    } catch (e) {
      console.error(e);
      msg.textContent = L("failed");
    }
  })();
})();
