(function () {
  function loadInstagramOnce() {
    if (window.__igLoaded) return;
    window.__igLoaded = true;
    const s = document.createElement('script');
    s.src = 'https://www.instagram.com/embed.js';
    s.async = true;
    document.body.appendChild(s);
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Ajusta esta lectura de consentimiento a tu lógica real
    const consentRaw = localStorage.getItem('ck-consent-v1');
    let wantsMarketing = false;
    try { wantsMarketing = consentRaw && JSON.parse(consentRaw).marketing === true; } catch (e) {}

    const target = document.querySelector('.instagram-media, blockquote[data-instgrm-permalink]');
    if (!wantsMarketing || !target) return;

    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(entries => {
        if (entries.some(e => e.isIntersecting)) {
          io.disconnect();
          loadInstagramOnce();
        }
      });
      io.observe(target);
    } else {
      loadInstagramOnce();
    }
  });
})();
