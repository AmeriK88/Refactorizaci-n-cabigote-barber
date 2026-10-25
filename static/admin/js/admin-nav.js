/*
 * Navegación responsive de Ca'Bigote.
 * Reutiliza el #nav-sidebar y el #toggle-nav-sidebar nativos de Django: por debajo de 1280 px
 * (el mismo punto en el que django-admin-interface oculta la barra) la barra pasa a ser un panel
 * deslizante modal. En escritorio no hace nada y la lógica nativa (nav_sidebar.js) sigue intacta.
 */
(() => {
  const NARROW_QUERY = "(max-width: 1279px)"; // debe coincidir con el @media de adminDashboard.css
  const OPEN_CLASS = "cb-nav-open";
  const LOCK_CLASS = "cb-nav-lock";
  const LABELS = { title: "Navegación", close: "Cerrar" };
  const FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

  const toggle = document.getElementById("toggle-nav-sidebar");
  const sidebar = document.getElementById("nav-sidebar");
  const main = document.getElementById("main");
  const branding = document.getElementById("branding");
  if (!toggle || !sidebar || !main || !branding) return;

  const query = window.matchMedia(NARROW_QUERY);
  let isOpen = false;
  let inertTargets = [];

  const header = document.createElement("div");
  header.className = "cb-nav-header";
  const title = document.createElement("span");
  title.className = "cb-nav-title";
  title.textContent = LABELS.title;
  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.className = "cb-nav-close";
  closeButton.textContent = LABELS.close;
  closeButton.setAttribute("aria-label", `${LABELS.close} ${LABELS.title.toLowerCase()}`);
  header.append(title, closeButton);
  sidebar.prepend(header);

  const backdrop = document.createElement("div");
  backdrop.className = "cb-nav-backdrop";
  backdrop.hidden = true;
  document.body.append(backdrop);

  const setInert = (value) => {
    if (value) {
      const container = document.getElementById("container");
      inertTargets = [
        ...(container ? [...container.children].filter((node) => node !== main) : []),
        document.getElementById("content-start"),
        document.querySelector(".skip-to-content-link"),
      ].filter(Boolean);
      inertTargets.forEach((node) => node.setAttribute("inert", ""));
    } else {
      inertTargets.forEach((node) => node.removeAttribute("inert"));
      inertTargets = [];
    }
  };

  const open = () => {
    if (isOpen) return;
    isOpen = true;
    main.classList.add(OPEN_CLASS);
    backdrop.hidden = false;
    document.documentElement.classList.add(LOCK_CLASS);
    toggle.setAttribute("aria-expanded", "true");
    setInert(true);
    sidebar.scrollTop = 0;
    closeButton.focus();
  };

  const close = ({ restoreFocus = true } = {}) => {
    if (!isOpen) return;
    isOpen = false;
    main.classList.remove(OPEN_CLASS);
    backdrop.hidden = true;
    document.documentElement.classList.remove(LOCK_CLASS);
    toggle.setAttribute("aria-expanded", "false");
    setInert(false);
    if (restoreFocus) toggle.focus();
  };

  // En pantallas estrechas el botón nativo vive en la cabecera; en escritorio vuelve a su sitio.
  const placeToggle = () => {
    if (query.matches) {
      if (toggle.parentElement !== branding) branding.prepend(toggle);
      toggle.setAttribute("aria-controls", "nav-sidebar");
      toggle.setAttribute("aria-expanded", String(isOpen));
    } else {
      close({ restoreFocus: false });
      if (toggle.parentElement !== main) main.insertBefore(toggle, sidebar);
      toggle.removeAttribute("aria-controls");
      toggle.removeAttribute("aria-expanded");
    }
  };

  // Captura en document: se ejecuta antes que el manejador nativo, que solo debe actuar en escritorio.
  document.addEventListener(
    "click",
    (event) => {
      if (!query.matches || !(event.target instanceof Element)) return;
      if (event.target.closest("#toggle-nav-sidebar")) {
        event.stopPropagation();
        isOpen ? close() : open();
      }
    },
    true,
  );

  closeButton.addEventListener("click", () => close());
  backdrop.addEventListener("click", () => close());

  document.addEventListener("keydown", (event) => {
    if (!isOpen) return;
    if (event.key === "Escape") {
      event.preventDefault();
      close();
      return;
    }
    if (event.key !== "Tab") return;
    const items = [...sidebar.querySelectorAll(FOCUSABLE)].filter((node) => node.offsetParent !== null);
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  sidebar.addEventListener("click", (event) => {
    if (isOpen && event.target instanceof Element && event.target.closest("a[href]")) {
      close({ restoreFocus: false });
    }
  });

  query.addEventListener("change", placeToggle);
  placeToggle();
})();
