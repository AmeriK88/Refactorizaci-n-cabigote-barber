// static/js/pwa-install.js
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn-instalar");
  if (!btn) return;

  let deferredPrompt = null;

  const isStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true; // iOS

  const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const isSafari = isIOS && /safari/i.test(navigator.userAgent) && !/crios|fxios/i.test(navigator.userAgent);

  // 1) Si ya está instalada, fuera botón
  if (isStandalone) {
    btn.classList.add("d-none");
    return;
  }

  // 2) Si NO está instalada, mostramos el botón SIEMPRE
  // (así no dependes de que Chrome dispare beforeinstallprompt)
  btn.classList.remove("d-none");

  // 3) Capturamos el evento de instalación cuando exista (Chrome/Edge/Android)
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // botón ya visible, pero así sabes que habrá prompt real
    btn.dataset.canPrompt = "1";
  });

  // 4) Click del botón: prompt real o instrucciones iOS
  btn.addEventListener("click", async () => {
    // Chrome/Edge con prompt disponible
    if (deferredPrompt) {
      btn.disabled = true;
      deferredPrompt.prompt();

      try {
        const { outcome } = await deferredPrompt.userChoice;
        deferredPrompt = null;

        if (outcome === "accepted") btn.classList.add("d-none");
      } finally {
        btn.disabled = false;
      }
      return;
    }

    // iOS Safari: no hay prompt, mostramos guía
    if (isSafari) {
      alert("En iPhone: pulsa Compartir (⬆️) → 'Añadir a pantalla de inicio'.");
      return;
    }

    // Otros casos: el navegador no ofrece prompt (rechazado antes o no elegible)
    alert("Tu navegador no permite instalar ahora mismo. Prueba a actualizar, usar Chrome/Edge o revisar si ya está instalada.");
  });

  // 5) Si se instala, ocultamos botón
  window.addEventListener("appinstalled", () => {
    btn.classList.add("d-none");
    deferredPrompt = null;
  });

  // 6) Tu lógica de SW + actualización (con guard para no recargar en la primera instalación)
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js", { updateViaCache: "none" })
        .then((reg) => {
          console.log("SW registrado:", reg);

          reg.addEventListener("updatefound", () => {
            const newWorker = reg.installing;
            if (!newWorker) return;

            newWorker.addEventListener("statechange", () => {
              if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
                newWorker.postMessage({ type: "SKIP_WAITING" });
              }
            });
          });

          // CLAVE: solo recargar si ya había un SW controlando antes
          let hadController = !!navigator.serviceWorker.controller;
          navigator.serviceWorker.addEventListener("controllerchange", () => {
            if (hadController) window.location.reload();
            hadController = true;
          });
        })
        .catch((err) => console.error("Error SW:", err));
    });
  }
});
