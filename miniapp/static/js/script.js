// === ВЕРХ ФАЙЛА ===
let currentPage = 1;
let totalPages = 1;
let loading = false;
const CAT = (window.CAT || "listing").toLowerCase();
const APP_LANG = (window.APP_LANG || "uk").toLowerCase();
window.SORT_FIELD = typeof window.SORT_FIELD === "string" ? window.SORT_FIELD : "date"; // date|price|area|rooms|id|saved
window.SORT_DIR   = (window.SORT_DIR === "asc" || window.SORT_DIR === "desc") ? window.SORT_DIR : "desc";
const SORT_FIELDS = ["date","price","area","rooms","id","saved"];

function sortPayload() {
  const field = SORT_FIELDS.includes(window.SORT_FIELD) ? window.SORT_FIELD : "date";
  const dir   = (window.SORT_DIR === "asc") ? "asc" : "desc";
  return { sort_field: field, sort_dir: dir };
}

let tg, initData;
let totalCountElem = null;

/* ================== I18N ================== */
const I18N = {
  uk: {
    apartment: "квартира",
    house: "будинок",
    room: "кімната",
    remove: "Видалити",
    save: "Зберегти",
    no_commission: "без комісії",
    commission: "комісія",
    on_map: "На карті",
    contact: "Зв’язок",
    more: "Детальніше",
    hide: "Згорнути",
    no_photo: "Без фото",
    nothing_found: "Нічого не знайдено",
    ad_removed: "Оголошення було видалене",
    link_unavailable: "Посилання недоступне",
    no_subscription_title: "У тебе немає підписки",
    no_subscription_msg: "Для доступу до контактів треба оформити підписку Domio",
    no_full_sub_msg: "Ця функція доступна лише в повному доступі!",
    pay_action: "Оформити",
    cancel_action: "Скасувати",
    pay_called_try_close: "Оплата викликана, намагаюся закрити WebApp",
    pay_failed: "Не вдалося викликати оплату",
    user_cancelled: "Користувач скасував оплату.",
    load_error: "Помилка завантаження оголошень",
    save_error: "Помилка при збереженні",
    // Заголовки:
    title_last_week: "об’єкти, додані за останній тиждень",
    title_saved: "збережені об’єкти",
    title_found: "за твоїми фільтрами знайдено об’єкти без комісії",
    // Единицы
    area_unit: "м²",
    // Debug/варнинги
    not_in_tg: "Не в Telegram WebApp або не завантажено telegram-web-app.js",
  },
  en: {
    apartment: "apartment",
    house: "house",
    room: "room",
    remove: "Remove",
    save: "Save",
    no_commission: "no commission",
    commission: "commission",
    on_map: "On map",
    contact: "Contact",
    more: "More",
    hide: "Hide",
    no_photo: "No photo",
    nothing_found: "Nothing found",
    ad_removed: "The listing was removed",
    link_unavailable: "Link is unavailable",
    no_subscription_title: "No subscription",
    no_subscription_msg: "To access contacts, please subscribe to Domio",
    no_full_sub_msg: "This feature is available only with full access!",
    pay_action: "Subscribe",
    cancel_action: "Cancel",
    pay_called_try_close: "Payment triggered, trying to close WebApp",
    pay_failed: "Failed to trigger payment",
    user_cancelled: "User canceled payment.",
    load_error: "Failed to load listings",
    save_error: "Error while saving",
    // Titles:
    title_last_week: "properties added in the last week",
    title_saved: "saved properties",
    title_found: "properties without commission found by your filters",
    // Units
    area_unit: "m²",
    // Warnings
    not_in_tg: "Not in Telegram WebApp or telegram-web-app.js not loaded",
  },
  pl: {
    apartment: "mieszkanie",
    house: "dom",
    room: "pokój",
    remove: "Usuń",
    save: "Zapisz",
    no_commission: "bez prowizji",
    commission: "prowizji",
    on_map: "Na mapie",
    contact: "Kontakt",
    more: "Więcej",
    hide: "Zwiń",
    no_photo: "Brak zdjęcia",
    nothing_found: "Nic nie znaleziono",
    ad_removed: "Ogłoszenie zostało usunięte",
    link_unavailable: "Link niedostępny",
    no_subscription_title: "Brak subskrypcji",
    no_subscription_msg: "Aby uzyskać dostęp do kontaktów, wykup subskrypcję Domio",
    no_full_sub_msg: "Ta funkcja jest dostępna tylko w ramach pełnego dostępu!",
    pay_action: "Wykup",
    cancel_action: "Anuluj",
    pay_called_try_close: "Płatność wywołana, próbuję zamknąć WebApp",
    pay_failed: "Nie udało się wywołać płatności",
    user_cancelled: "Użytkownik anulował płatność.",
    load_error: "Błąd ładowania ogłoszeń",
    save_error: "Błąd zapisu",
    // Tytuły:
    title_last_week: "nieruchomości dodane w ostatnim tygodniu",
    title_saved: "zapisane nieruchomości",
    title_found: "według Twoich filtrów znaleziono nieruchomości bez prowizji",
    // Jednostki
    area_unit: "m²",
    // Ostrzeżenia
    not_in_tg: "Nie w Telegram WebApp albo nie załadowano telegram-web-app.js",
  },
};

function t(key) {
  const lang = I18N[APP_LANG] ? APP_LANG : "uk";
  return (I18N[lang] && I18N[lang][key]) ?? (I18N.uk[key] ?? key);
}
/* ================== /I18N ================== */

// Передаём pageTag внутрь карточки!
function renderApartment(a, pageTag) {
  const container = document.getElementById("apartments");
  const col = document.createElement("div");
  col.className = "card";
  col.id = `apartment-${a.base_id}`;
  const index = `${a.base_id}`;

  const isSaved = a.saved === true;
  const saveText = isSaved ? t('remove') : t('save');
  const saveIcon = isSaved ? '/miniapp/static/images/remove.png' : '/miniapp/static/images/save.png';
  const mapq = a.address?.trim() || a.city_distr?.trim() || "";
  const commissionText = a.no_comission ? t('no_commission') : t('commission');
  const propertyType = a.property_type ? t(a.property_type) : "";
  col.innerHTML = `
    <div class="swiper swiper-container" id="swiper-${pageTag}-${index}">
      <div class="swiper-wrapper">
        ${
          Array.isArray(a.images) && a.images.length
            ? a.images.map(img => `
              <div class="swiper-slide">
                <div class="swiper-slide-img-wrapper">
                  <div class="swiper-zoom-container">
                    <img class="swiper-zoom-target" src="${img}?w=800" alt="Фото" loading="lazy" decoding="async">
                  </div>
                </div>
              </div>`).join('')
            : `
              <div class="swiper-slide">
                <div class="swiper-slide-img-wrapper">
                  <div class="swiper-zoom-container">
                    <img class="swiper-zoom-target" src="https://via.placeholder.com/600x400?text=${encodeURIComponent(t('no_photo'))}" alt="${t('no_photo')}">
                  </div>
                </div>
              </div>`
        }
      </div>
      <div class="swiper-button-prev custom-swiper-btn">
        <img src="/miniapp/static/images/arrow-left.png" alt="prev" />
      </div>
      <div class="swiper-button-next custom-swiper-btn">
        <img src="/miniapp/static/images/arrow-right.png" alt="next" />
      </div>
      <div class="swiper-scrollbar"></div>
    </div>
    <div class="card-body">
    <div class="card-info-row">
      <div class="card-base-info">
        <div class="price-row">
          <span class="card-price">${a.price}</span>
          <div class="card-comission-info">
            <img src="/miniapp/static/images/percent.png" class="icon" alt="">
            <span>${commissionText}</span>
          </div>
        </div>
        <span class="card-address">${a.city_distr}</span>
        <!--<span class="card-address">${a.address}</span>-->
        <!--<span class="card-city_distr">${a.city_distr}</span>-->
      </div>
    </div>

    <div class="card-meta-row">
      <div class="card-meta-item">
        <img src="/miniapp/static/images/rooms.png" class="icon" alt="">
        <span>${a.rooms}</span>
      </div>
      ${propertyType ? `
      <div class="card-meta-item">
        <img src="/miniapp/static/images/type.png" class="icon" alt="">
        <span>${propertyType}</span>
      </div>` : ""}
      <div class="card-meta-item">
        <img src="/miniapp/static/images/area.png" class="icon" alt="">
        <span>${a.area} ${t('area_unit')}</span>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-sm btn-outline-secondary" onclick="openMap('${mapq}')">
        ${t('on_map')} <img src="/miniapp/static/images/map.png" class="icon" alt="">
      </button>

      <button class="btn btn-sm btn-outline-secondary save-btn" 
              data-id="${a.base_id}" 
              data-saved="${isSaved}" 
              onclick="toggleSave(this)">
        ${saveText} <img src="${saveIcon}" class="icon" alt="">
      </button>

      <button class="btn btn-sm btn-outline-secondary"
              data-id="${a.base_id}" 
              onclick="openContact(this)">
        ${t('contact')} <img src="/miniapp/static/images/contact.png" class="icon" alt="">
      </button>

      <button class="btn btn-sm btn-outline-secondary" onclick="toggleDescription('desc-${pageTag}-${index}', this)">
        ${t('more')} <img src="/miniapp/static/images/more.svg" class="icon" alt="">
      </button>
    </div>

    <div class="description-container">
      <div class="description-text" id="desc-${pageTag}-${index}">
        <p class="card-text">${a.description}</p>
      </div>
    </div>
  </div>
  `;

  container.appendChild(col);
  requestAnimationFrame(() => col.classList.add('appeared'));

  new Swiper(`#swiper-${pageTag}-${index}`, {
    slidesPerView: 1,
    spaceBetween: 8,
    autoHeight: true,
    navigation: {
      nextEl: `#swiper-${pageTag}-${index} .swiper-button-next`,
      prevEl: `#swiper-${pageTag}-${index} .swiper-button-prev`,
    },
    preloadImages: false,  // важно для lazy
    lazy: {
      loadPrevNext: true,
      loadPrevNextAmount: 2,
      loadOnTransitionStart: true
    },
    scrollbar: {
      el: `#swiper-${pageTag}-${index} .swiper-scrollbar`,
      draggable: true,
      hide: false
    },
    // ⬇️ добавлено
    zoom: {
      maxRatio: 3,     // во сколько раз увеличивать
      toggle: true     // разрешить переключать зум кликом/тапом
    },
    on: {
      // Делаем зум по одному клику (по умолчанию — даблтап)
      click(swiper, e) {
        const inZoomArea = e.target.closest('.swiper-zoom-container');
        if (!inZoomArea) return;
        const scale = swiper.zoom.scale || 1;
        if (scale === 1) swiper.zoom.in(e);
        else swiper.zoom.out();
      }
    }
  });
}


function toggleDescription(id, btn) {
  const desc = document.getElementById(id);
  desc.classList.toggle("expanded");

  const isExpanded = desc.classList.contains("expanded");
  const iconPath = isExpanded ? "/miniapp/static/images/hide.svg" : "/miniapp/static/images/more.svg";

  btn.innerHTML = `${isExpanded ? t('hide') : t('more')} <img src="${iconPath}" class="icon" alt="">`;
}


function openMap(address) {
  const encoded = encodeURIComponent(address);
  const url = `https://www.google.com/maps/search/?api=1&query=${encoded}`;
  tg.openLink(url);
}


async function triggerInvoice(initData, base_id) {
  const response = await fetch('/api/trigger_invoice', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": tg.initData
    },
    body: JSON.stringify({
      lang: APP_LANG,
      ...sortPayload()
    }),
  });
  return response;
}


async function openContact(btn) {
  const id = btn.dataset.id;
  try {
    const response = await fetch(`/api/get_link`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": tg.initData
      },
      body: JSON.stringify({
        base_id: Number(id),
        lang: APP_LANG,
        ...sortPayload()
      })
    });

    if (response.status === 403) {
      showPaymentPopup(id);
      return;
    }

    if (response.status === 410) {
      const card = document.getElementById(`apartment-${id}`);
      if (card) card.remove();
      alert(t('ad_removed'));
      return;
    }

    if (response.status === 200) {
      const data = await response.json();
      const url = data.url;
      if (url) {
        tg.openLink(url);
      } else {
        alert(t('link_unavailable'));
      }
    } else {
      console.error(`Unexpected response: ${response.status}`);
    }
  } catch (error) {
    console.error("Request failed:", error);
  }
}


async function toggleSave(btn) {
  const id = btn.dataset.id;
  const isSaved = btn.dataset.saved === "true";
  const action = isSaved ? "remove" : "save";
  try {
    const response = await fetch(`/api/toggle_save`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": tg.initData
      },
      body: JSON.stringify({
        base_id: Number(id),
        action: action,
        lang: APP_LANG,
        ...sortPayload()
      })
    });

    if (response.status === 403) {
      showPaymentPopup(id, true);
      return;
    }

    if (response.status === 410) {
      const card = document.getElementById(`apartment-${id}`);
      if (card) card.remove();
      alert(t('ad_removed'));
      return;
    }

    if (!response.ok) {
      console.error(`Unexpected response: ${response.status}`);
      return;
    }

    // Успешный ответ, обновляем кнопку
    btn.dataset.saved = (!isSaved).toString();
    btn.innerHTML = (!isSaved ? t('remove') : t('save')) +
      ` <img src="${!isSaved
        ? '/miniapp/static/images/remove.png'
        : '/miniapp/static/images/save.png'}" class="icon" alt="">`;

  } catch (error) {
    console.error(t('save_error') + ":", error);
  }
}


function showPaymentPopup(baseId, is_full = false) {
  window.lastBaseIdForInvoice = baseId;
  const message = is_full
    ? t('no_full_sub_msg')      // если is_full === true
    : t('no_subscription_msg'); // иначе
  tg.showPopup({
    title: t('no_subscription_title'),
    message: message,
    buttons: [
      { id: "pay", type: "default", text: t('pay_action') },
      { id: "cancel", type: "destructive", text: t('cancel_action') }
    ]
  });
}

function setTitle(total = null) {
  const el = document.getElementById('total-title');
  if (!el) return;

  let baseText;
  if (CAT === 'last_week') {
    baseText = t('title_last_week');
  } else if (CAT === 'saved') {
    baseText = t('title_saved');
  } else {
    baseText = t('title_found');
  }

  if (total == null) {
    el.innerHTML = `${baseText}`;
    totalCountElem = null;
  } else {
    el.innerHTML = `${baseText}: <span id="total-count" class="highlight-total">${total}</span>`;
    totalCountElem = document.getElementById('total-count');
  }
}

// === ПАГИНАЦИЯ ЗАГРУЗКИ СТРАНИЦЫ ===
async function loadPage(p = 1, { scrollToCards = true } = {}) {
  if (loading) return;
  loading = true;
  const container = document.getElementById("apartments");
  try {
    const response = await fetch(`/api/apartments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": tg.initData
      },
      body: JSON.stringify({
        page: Number(p),
        cat: CAT,
        lang: APP_LANG,
        ...sortPayload()
      })
    });

    if (!response.ok) {
      const txt = await response.text();
      console.error(`Помилка запиту: ${response.status}`, txt);
      return;
    }

    const data = await response.json();

    totalPages = Number(data.total_page) || 1;

    if (p === 1 && typeof data.total === "number") {
      setTitle(data.total);
    }

    container.innerHTML = "";
    if (Array.isArray(data.results) && data.results.length) {
      data.results.forEach(item => renderApartment(item, p));
    } else {
      container.innerHTML = `<div class="text-center empty-state">${t('nothing_found')}</div>`;
    }

    currentPage = p;
    renderPagination();
    if (scrollToCards) {
      const firstCard = document.querySelector("#apartments .card");
      if (firstCard) {
        const y = firstCard.getBoundingClientRect().top + window.pageYOffset - 40;
        window.scrollTo({ top: y, behavior: "smooth" });
      }
    }

  } catch (err) {
    console.error(t('load_error') + ":", err);
  } finally {
    loading = false;
  }
}


function renderPagination() {
  const el = document.getElementById("pagination");
  if (!el) return;

  const maxButtons = 7;
  let start = Math.max(1, currentPage - Math.floor(maxButtons / 2));
  let end = start + maxButtons - 1;
  if (end > totalPages) {
    end = totalPages;
    start = Math.max(1, end - maxButtons + 1);
  }

  let html = "";
  html += `<button class="page-btn" data-page="${currentPage - 1}" ${currentPage === 1 ? "disabled" : ""}>‹</button>`;

  if (start > 1) {
    html += `<button class="page-btn" data-page="1" type="button">1</button>`;
    if (start > 2) html += `<span class="ellipsis">…</span>`;
  }

  for (let i = start; i <= end; i++) {
    html += `<button class="page-btn ${i === currentPage ? "active" : ""}" data-page="${i}" type="button">${i}</button>`;
  }

  if (end < totalPages) {
    if (end < totalPages - 1) html += `<span class="ellipsis">…</span>`;
    html += `<button class="page-btn" data-page="${totalPages}" type="button">${totalPages}</button>`;
  }

  html += `<button class="page-btn" data-page="${currentPage + 1}" ${currentPage === totalPages ? "disabled" : ""} type="button">›</button>`;
  el.innerHTML = html;
}



const I18N_SORT = {
  uk: {
    asc: "За зростанням",
    desc: "За спаданням",
    descHint: "За замовчуванням — за спаданням (DESC)",
    fields: {
      date: "Дата",
      price: "Ціна",
      area: "Площа",
      rooms: "Кімнати",
      id: "ID",
      saved: "Збережено"
    }
  },
  pl: {
    asc: "Rosnąco",
    desc: "Malejąco",
    descHint: "Domyślnie — malejąco (DESC)",
    fields: {
      date: "Data",
      price: "Cena",
      area: "Powierzchnia",
      rooms: "Pokoje",
      id: "ID",
      saved: "Zapisano"
    }
  },
  en: {
    asc: "ASC",
    desc: "DESC",
    descHint: "Default — DESC",
    fields: {
      date: "Date",
      price: "Price",
      area: "Area",
      rooms: "Rooms",
      id: "ID",
      saved: "Saved"
    }
  }
};


function applySortingI18n() {
  const lang = (window.APP_LANG || "uk").toLowerCase();
  const T = I18N_SORT[lang] || I18N_SORT.uk;

  const bar = document.getElementById("sorting-toolbar");
  if (!bar) return;

  // Хинт
  const hintEl = bar.querySelector('.sort-hint, [data-i18n="descHint"]');
  if (hintEl) {
    hintEl.setAttribute("data-i18n", "descHint");
    hintEl.textContent = T.descHint;
  }

  // Опции селекта поля
  const sf = bar.querySelector("#sf-select");
  if (sf) {
    const FIELD_LABELS = {
      date:  T.fields.date,
      price: T.fields.price,
      area:  T.fields.area,
      rooms: T.fields.rooms,
      id:    T.fields.id,
      saved: T.fields.saved,
    };
    Array.prototype.forEach.call(sf.options, function (opt) {
      if (FIELD_LABELS[opt.value]) opt.textContent = FIELD_LABELS[opt.value];
    });
  }

  // Опции селекта направления
  const sd = bar.querySelector("#sd-select");
  if (sd) {
    Array.prototype.forEach.call(sd.options, function (opt) {
      opt.textContent = (opt.value === "asc") ? T.asc : T.desc;
    });
  }
}

// инициализация сортировки (2 селекта) + автообновление
function initSortingToolbar() {
  const sf = document.getElementById("sf-select"); // поле
  const sd = document.getElementById("sd-select"); // направление
  if (!sf || !sd) return;

  // скрыть "saved" если не та категория
  const savedOpt = sf.querySelector('option[value="saved"]');
  if (savedOpt) savedOpt.hidden = (CAT !== "saved");

  // выставить текущие значения
  sf.value = SORT_FIELDS.includes(window.SORT_FIELD) ? window.SORT_FIELD : "date";
  sd.value = (window.SORT_DIR === "asc") ? "asc" : "desc";

  // лёгкий дебаунс, чтобы не спамить запросами
  let reloadTimer;
  const reload = () => {
    clearTimeout(reloadTimer);
    reloadTimer = setTimeout(() => loadPage(1, { scrollToCards: false }), 60);
  };

  // изменение поля
  sf.addEventListener("change", () => {
    window.SORT_FIELD = sf.value;
    reload();
  });

  // изменение направления
  sd.addEventListener("change", () => {
    window.SORT_DIR = sd.value;
    reload();
  });
}

window.addEventListener('DOMContentLoaded', () => {
  initSortingToolbar();       // <— тут
  applySortingI18n?.();
  if (!window.Telegram || !Telegram.WebApp) {
    console.warn(t('not_in_tg'));
    return;
  }
  tg = Telegram.WebApp;
  initData = tg.initDataUnsafe;
  console.log(APP_LANG, CAT)
  tg.expand();

  tg.onEvent('popupClosed', (eventData) => {
    if (eventData.button_id === 'pay') {
      triggerInvoice(initData, window.lastBaseIdForInvoice)
        .then(() => {
          console.log(t('pay_called_try_close'));
          tg.close();
        })
        .catch((err) => {
          console.error(t('pay_failed') + ":", err);
        });
    } else if (eventData.button_id === 'cancel') {
      console.log(t('user_cancelled'));
    }
  });

  const pag = document.getElementById("pagination");
  if (pag) {
    pag.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-page]");
      if (!btn) return;
      const p = Number(btn.dataset.page);
      if (!Number.isFinite(p) || p < 1 || p > totalPages || p === currentPage) return;
      loadPage(p);
    });
  }

  loadPage(1, { scrollToCards: false });
});
