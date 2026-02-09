document.addEventListener("DOMContentLoaded", () => {
  const modalEl = document.getElementById("specialMessageModal");
  if (!modalEl) return;

  const messageId = modalEl.getAttribute("data-message-id");
  if (!messageId) return;

  // clave por ID (no lista infinita)
  const storageKey = `special_message_closed_${messageId}`;

  // Si ya lo cerró una vez, no lo vuelvas a mostrar
  if (localStorage.getItem(storageKey) === "1") return;

  const bsModal = new bootstrap.Modal(modalEl, {
    backdrop: true,
    keyboard: true,
    focus: true,
  });

  bsModal.show();

  // solo marcamos como “visto” cuando realmente se cierra
  modalEl.addEventListener("hidden.bs.modal", () => {
    localStorage.setItem(storageKey, "1");
  });

  // ---------- LOTTIE (opcional) ----------
  const showLottie = modalEl.getAttribute("data-show-lottie") === "1";
  if (!showLottie) return;

  const container = document.getElementById("specialMessageLottie");
  if (!container) return;

  const path = container.getAttribute("data-lottie-path");
  if (!path) return;

  // Si no está cargado lottie.min.js, no rompemos nada
  if (typeof window.lottie === "undefined") return;

  try {
    window.lottie.loadAnimation({
      container,
      renderer: "svg",
      loop: true,
      autoplay: true,
      path,
    });
  } catch (e) {
    console.warn("Lottie load failed:", e);
  }
});
