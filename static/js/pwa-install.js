/* PWA - Instalación “Add to Home Screen” */
document.addEventListener('DOMContentLoaded', () => {
  let deferredPrompt;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();                // Bloquea el banner automático
    deferredPrompt = e;                // Guarda el evento
    document.getElementById('btn-instalar').classList.remove('d-none');
  });

  document.getElementById('btn-instalar').addEventListener('click', async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();           // Lanza el diálogo nativo
    await deferredPrompt.userChoice;   // Espera la elección del usuario
    deferredPrompt = null;             // Limpia
    document.getElementById('btn-instalar').classList.add('d-none');
  });

  window.addEventListener('appinstalled', () => {
    document.getElementById('btn-instalar').classList.add('d-none'); // Oculta si ya está instalada
  });
});
