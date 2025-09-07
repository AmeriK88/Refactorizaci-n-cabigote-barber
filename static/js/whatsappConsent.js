/* whatsappConsent.js — Ca'Bigote */
(function () {
  const waBtn = document.getElementById('whatsapp-btn');
  const modalEl = document.getElementById('wa-modal');
  if (!waBtn || !modalEl) return;

  const modal = () => bootstrap.Modal.getOrCreateInstance(modalEl);
  const checkbox = modalEl.querySelector('#wa-accept');
  const continueBtn = modalEl.querySelector('#wa-continue');

  // Habilita/deshabilita el botón de continuar según el checkbox
  checkbox?.addEventListener('change', () => {
    continueBtn.disabled = !checkbox.checked;
  });

  // Intercepta el click del botón flotante
  waBtn.addEventListener('click', (e) => {
    // Si ya aceptó previamente en esta sesión, deja pasar:
    if (sessionStorage.getItem('wa-accepted') === '1') return;
    e.preventDefault();
    // Abre modal
    checkbox.checked = false;
    continueBtn.disabled = true;
    modal().show();
  });

  // Continuar a WhatsApp
  continueBtn.addEventListener('click', () => {
    const href = waBtn.getAttribute('href');
    sessionStorage.setItem('wa-accepted', '1');
    modal().hide();
    // Redirige
    window.open(href, '_blank', 'noopener');
  });
})();
