// === ВЕРХ ФАЙЛА ===
let currentPage = 1;
let totalPages = 1;
let loading = false;
const CAT = window.CAT ?? "";

let tg, initData;
let totalCountElem = null;



// Передаём pageTag внутрь карточки!
function renderApartment(a, pageTag) {
  const container = document.getElementById("apartments");
  const col = document.createElement("div");
  col.className = "card";
  col.id = `apartment-${a.base_id}`;
  const index = `${a.base_id}`;

  const isSaved = a.saved === true;
  const saveText = isSaved ? 'Видалити' : 'Зберегти';
  const saveIcon = isSaved ? '/miniapp/static/images/remove.png' : '/miniapp/static/images/save.png';
  const mapq = [a.city_distr, a.address].filter(Boolean).join(', ');
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
                    <img class="swiper-zoom-target" src="https://via.placeholder.com/600x400?text=Без+фото" alt="Без фото">
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
            <span>без комісії</span>
          </div>
        </div>
        <span class="card-address">${a.address}</span>
        <span class="card-city_distr">${a.city_distr}</span>
      </div>
    </div>

    <div class="card-meta-row">
      <div class="card-meta-item">
        <img src="/miniapp/static/images/rooms.png" class="icon" alt="">
        <span>${a.rooms}</span>
      </div>
      <div class="card-meta-item">
        <img src="/miniapp/static/images/area.png" class="icon" alt="">
        <span>${a.area} м²</span>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-sm btn-outline-secondary" onclick="openMap('${mapq}')">
        На карті <img src="/miniapp/static/images/map.png" class="icon" alt="">
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
        Зв’язок <img src="/miniapp/static/images/contact.png" class="icon" alt="">
      </button>

      <button class="btn btn-sm btn-outline-secondary" onclick="toggleDescription('desc-${pageTag}-${index}', this)">
        Детальніше <img src="/miniapp/static/images/more.svg" class="icon" alt="">
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

  btn.innerHTML = `Детальніше <img src="${iconPath}" class="icon" alt="">`;

}


function openMap(address) {
  const encoded = encodeURIComponent(address);
  const url = `https://www.google.com/maps/search/?api=1&query=${encoded}`;
  tg.openLink(url);
}


function triggerInvoice(initData, base_id) {

  response = fetch('/api/trigger_invoice', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": tg.initData
    },
    body: JSON.stringify({
      init_data: initData,
      check_data: tg.initData}),
    
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
        base_id: id,
      })
    });

    if (response.status === 403) {
      showPaymentPopup(id);
      return;
    }

    if (response.status === 410) {
      // Удаляем карточку из DOM
      const card = document.getElementById(`apartment-${id}`);
      if (card) card.remove();
      alert("Оголошення було видалене")
      return;
    }

    if (response.status === 200) {
      const data = await response.json();
      const url = data.url;
      if (url) {
        tg.openLink(url);
        //window.open(url, "_blank");
      } else {
        alert("Посилання недоступне");
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
      headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": tg.initData},
      body: JSON.stringify({
        init_data: initData,
        base_id: id,
        action: action,
        check_data: tg.initData
      })
    });

    if (response.status === 403) {
      showPaymentPopup(id);
      return;
    }

    if (response.status === 410) {
      // Удаляем карточку из DOM
      const card = document.getElementById(`apartment-${id}`);
      if (card) card.remove();
      alert("Оголошення було видалене");
      return;
    }

    if (!response.ok) {
      console.error(`Unexpected response: ${response.status}`);
      return;
    }

    // Успешный ответ, обновляем кнопку
    btn.dataset.saved = (!isSaved).toString();
    btn.innerHTML = (!isSaved ? 'Видалити' : 'Зберегти') +
      ` <img src="${!isSaved
        ? '/miniapp/static/images/remove.png'
        : '/miniapp/static/images/save.png'}" class="icon" alt="">`;

  } catch (error) {
    console.error("Ошибка при сохранении:", error);
  }
}


function showPaymentPopup(baseId) {
  window.lastBaseIdForInvoice = baseId;
  tg.showPopup({
    title: "У тебе немає підписки",
    message: "Для доступу до контактів треба оформити підписку Findly: тестову за 1 грн на 7 днів або місячну за 249 грн.",
    buttons: [
      { id: "pay", type: "default", text: "Оформити" },
      { id: "cancel", type: "destructive", text: "Скасувати" }
    ]
  });
}

function setTitle(total = null) {
  const el = document.getElementById('total-title');
  if (!el) return;

  // текст в зависимости от CAT
  let baseText;
  if (CAT === 'last_week') {
    baseText = 'квартири, додані за останній тиждень';
  } else if (CAT === 'saved') {
    baseText = 'збережені квартири';
  } else {
    baseText = 'за твоїми фільтрами знайдено квартир без комісії';
  }

  // если total ещё не знаем — рисуем без числа
  if (total == null) {
    el.innerHTML = `${baseText}`;
    totalCountElem = null; // пока нет
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
      headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": tg.initData},
      body: JSON.stringify({
        page: p,
        cat: CAT,
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
      setTitle(data.total); // дорисовали число
    }

    container.innerHTML = "";
    if (Array.isArray(data.results) && data.results.length) {
      data.results.forEach(item => renderApartment(item, p)); // <-- передаём p!
    } else {
      container.innerHTML = `<div class="text-center" style="opacity:.8;margin:24px 0">Нічого не знайдено</div>`;
    }

    currentPage = p;
    renderPagination();
    // Прокрутка к первой карточке
    if (scrollToCards) {
      const firstCard = document.querySelector("#apartments .card");
      if (firstCard) {
        const y = firstCard.getBoundingClientRect().top + window.pageYOffset - 40; // небольшой отступ
        window.scrollTo({ top: y, behavior: "smooth" });
      }
    }

  } catch (err) {
    console.error("Помилка завантаження оголошень:", err);
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
    html += `<button class="page-btn" data-page="1">1</button>`;
    if (start > 2) html += `<span style="opacity:.7;padding:8px 6px">…</span>`;
  }

  for (let i = start; i <= end; i++) {
    html += `<button class="page-btn ${i === currentPage ? "active" : ""}" data-page="${i}">${i}</button>`;
  }

  if (end < totalPages) {
    if (end < totalPages - 1) html += `<span style="opacity:.7;padding:8px 6px">…</span>`;
    html += `<button class="page-btn" data-page="${totalPages}">${totalPages}</button>`;
  }

  html += `<button class="page-btn" data-page="${currentPage + 1}" ${currentPage === totalPages ? "disabled" : ""}>›</button>`;

  el.innerHTML = html;
}


window.addEventListener('DOMContentLoaded', () => {
  if (!window.Telegram || !Telegram.WebApp) {
    console.warn('Не в Telegram WebApp или не загружен telegram-web-app.js');
    return;
  }
  tg = Telegram.WebApp;
  initData = tg.initDataUnsafe;

  tg.expand();

  tg.onEvent('popupClosed', (eventData) => {

    if (eventData.button_id === 'pay') {
      triggerInvoice(initData, window.lastBaseIdForInvoice)
        .then(() => {
          console.log("Оплата вызвана, пытаюсь закрыть WebApp");
          tg.close();
        })
        .catch((err) => {
          console.error("Не вдалося викликати оплату:", err);
        });
    } else if (eventData.button_id === 'cancel') {
      // Можно закрыть popup или просто ничего не делать
      console.log("Користувач скасував оплату.");
    }
  });

  // делегирование кликов по пагинации
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

  // первичная загрузка
  
  loadPage(1, { scrollToCards: false });
});
