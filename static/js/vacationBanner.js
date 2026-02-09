document.addEventListener("DOMContentLoaded", () => {
  const banner = document.getElementById("vacation-banner");
  if (!banner) return;

  // Persistencia: si el user lo cerró, no lo mostramos hasta que cambie el mensaje
  const messageId = banner.getAttribute("data-message-id") || "vacation";
  const storageKey = `vacation_banner_closed_${messageId}`;

  if (localStorage.getItem(storageKey) === "1") {
    banner.remove();
    return;
  }

  const closeBtn = document.getElementById("vacation-banner-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      localStorage.setItem(storageKey, "1");
      banner.remove();
    });
  }

  // Lottie
  const animContainer = document.getElementById("vacation-banner-anim");
  const lottieSrc = banner.getAttribute("data-lottie-src");

  // Si no hay lottie o no está cargado, no rompemos nada
  if (!animContainer || !lottieSrc || typeof window.lottie === "undefined") return;

  try {
    window.lottie.loadAnimation({
      container: animContainer,
      renderer: "svg",
      loop: true,
      autoplay: true,
      path: lottieSrc,
    });
  } catch (e) {
    // Silencioso: si falla el JSON, no queremos tumbar la web
    console.warn("Lottie banner failed:", e);
  }
});
