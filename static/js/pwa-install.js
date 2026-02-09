// static/js/pwa-install.js
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn-instalar");
  let deferredPrompt = null;

  if (!btn) return;

  // ---------- Helpers ----------
  const isStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true; // iOS Safari

  const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent);

  // Si ya está instalada, fuera
  if (isStandalone) {
    btn.classList.add("d-none");
    return;
  }

  // ---------- A2HS (Chrome/Edge/Android) ----------
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    btn.classList.remove("d-none");
  });

  btn.addEventListener("click", async () => {
    // Si tenemos prompt nativo (Chrome/Edge)
    if (deferredPrompt) {
      btn.disabled = true;
      deferredPrompt.prompt();

      const { outcome } = await deferredPrompt.userChoice;
      deferredPrompt = null;

      if (outcome === "accepted") btn.classList.add("d-none");
      btn.disabled = false;
      return;
    }

    // Fallback iOS (no existe beforeinstallprompt)
    if (isIOS) {
      alert("En iPhone/iPad: pulsa Compartir (⬆️) y luego “Añadir a pantalla de inicio”.");
      return;
    }

    // Otros casos: el navegador no ofrece prompt
    alert("Tu navegador no permite instalar ahora mismo (o ya se instaló antes).");
  });

  window.addEventListener("appinstalled", () => {
    btn.classList.add("d-none");
    deferredPrompt = null;
  });

  // ---------- Service Worker + “última versión” ----------
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", async () => {
      // IMPORTANTE: saber si ya había un SW controlando esta pestaña
      const hadController = !!navigator.serviceWorker.controller;

      try {
        const reg = await navigator.serviceWorker.register("/sw.js", {
          updateViaCache: "none",
        });

        // Detectar nueva versión
        reg.addEventListener("updatefound", () => {
          const newWorker = reg.installing;
          if (!newWorker) return;

          newWorker.addEventListener("statechange", () => {
            // Nuevo SW instalado + ya había uno controlando => UPDATE real
            if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
              newWorker.postMessage({ type: "SKIP_WAITING" });
            }
          });
        });

        // Solo recargamos si era un UPDATE real (no la primera instalación)
        let refreshing = false;
        navigator.serviceWorker.addEventListener("controllerchange", () => {
          if (!hadController) return; // <- clave
          if (refreshing) return;
          refreshing = true;
          window.location.reload();
        });
      } catch (err) {
        console.error("Error SW:", err);
      }
    });
  }
});
