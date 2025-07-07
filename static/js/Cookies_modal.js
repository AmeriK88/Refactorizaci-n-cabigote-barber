/* cookies-banner logic -------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {

  // 1️⃣ build the Bootstrap modal
  const modalEl     = document.getElementById('cookiesModal');
  const cookiesModal = new bootstrap.Modal(modalEl, { backdrop: 'static' });

  // 2️⃣ helper to store the choice
  const setPref = pref => {
    localStorage.setItem('cookiesPreference', pref);
    cookiesModal.hide();
    console.log(`Cookies ${pref}.`);
  };

  // 3️⃣ button events (once)
  modalEl.querySelector('.btn-primary')
         .addEventListener('click', () => setPref('accepted'));

  modalEl.querySelector('.btn-outline-secondary')
         .addEventListener('click', () => setPref('rejected'));

  // 4️⃣ show banner only if not decided, after page is idle/loaded
  const openIfNeeded = () => {
    if (!localStorage.getItem('cookiesPreference')) {
      modalEl.removeAttribute('inert');   // enable clicks & focus
      cookiesModal.show();
    }
  };

  ('requestIdleCallback' in window)
    ? requestIdleCallback(openIfNeeded, { timeout: 500 })
    : window.addEventListener('load', openIfNeeded);      

  // 5️⃣ privacy-policy link inside the banner
  document.getElementById('privacyPolicyLink')
          .addEventListener('click', e => {
            e.preventDefault();
            bootstrap.Modal.getOrCreateInstance('#privacyPolicyModal').show();
          });
});
