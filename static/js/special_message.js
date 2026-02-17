document.addEventListener("DOMContentLoaded", () => {
  const modalEl = document.getElementById("specialMessageModal");
  if (!modalEl) return;

  const messageId = modalEl.getAttribute("data-message-id");
  if (!messageId) return;

  const storageKey = `special_message_closed_${messageId}`;
  if (localStorage.getItem(storageKey) === "1") return;

  const bsModal = new bootstrap.Modal(modalEl, {
    backdrop: true,
    keyboard: true,
    focus: true,
  });

  // ---------- LOTTIE (opcional) ----------
  const showLottie = modalEl.getAttribute("data-show-lottie") === "1";
  let lottieAnim = null;

  const initLottie = () => {
    if (!showLottie) return;

    const container = document.getElementById("specialMessageLottie");
    if (!container) return;

    const path = container.getAttribute("data-lottie-path");
    if (!path) return;

    if (typeof window.lottie === "undefined") return;

    // evita doble init
    if (lottieAnim) return;

    try {
      lottieAnim = window.lottie.loadAnimation({
        container,
        renderer: "svg",
        loop: true,
        autoplay: true,
        path,
      });
    } catch (e) {
      console.warn("Lottie load failed:", e);
    }
  };

  bsModal.show();

  // ⬅️ Aquí está el cambio importante
  modalEl.addEventListener("shown.bs.modal", () => {
    initLottie();
  });

  modalEl.addEventListener("hidden.bs.modal", () => {
    localStorage.setItem(storageKey, "1");

    // opcional: limpiar animación
    if (lottieAnim) {
      lottieAnim.destroy();
      lottieAnim = null;
      const container = document.getElementById("specialMessageLottie");
      if (container) container.innerHTML = "";
    }
  });
});
