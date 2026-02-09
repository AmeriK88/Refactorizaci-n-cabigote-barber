// Registro del Service Worker (separado, fuera de posibles fallos de A2HS)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })
      .then((reg) => {
        console.log('SW registrado:', reg);

        // Detectar nueva versión
        reg.addEventListener('updatefound', () => {
          const newWorker = reg.installing;
          if (!newWorker) return;

          newWorker.addEventListener('statechange', () => {
            // Nuevo SW instalado y hay uno anterior controlando → update real
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Activar ya
              newWorker.postMessage({ type: 'SKIP_WAITING' });
            }
          });
        });
      })
      .catch((err) => console.error('Error SW:', err));

    // Cuando el SW nuevo toma control, recargamos para servir la versión nueva
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      window.location.reload();
    });
  });
}
