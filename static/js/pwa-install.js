/* pwa-install.js */
document.addEventListener('DOMContentLoaded', () => {
  const installBtn = document.getElementById('btn-instalar');
  let deferredPrompt;

  // A2HS
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) installBtn.classList.remove('d-none');
  });

  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      installBtn.classList.add('d-none');
      deferredPrompt = null;
    });
  }

  window.addEventListener('appinstalled', () => {
    if (installBtn) installBtn.classList.add('d-none');
  });
});

// Registro del Service Worker (separado, fuera de posibles fallos de A2HS)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })
      .then(reg => console.log('SW registrado:', reg))
      .catch(err => console.error('Error SW:', err));
  });
}
