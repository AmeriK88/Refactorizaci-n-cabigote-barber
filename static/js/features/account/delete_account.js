(function () {
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form.needs-validation');
    if (!form) return;

    const chk = document.getElementById('chkConfirm');
    const txt = document.getElementById('txtConfirm');
    const btn = document.getElementById('btnDelete');
    const msg = document.getElementById('msgError');
    const REQUIRED = (txt?.dataset.expected || 'ELIMINAR').toUpperCase();

    if (!chk || !txt || !btn || !msg) return;

    const showMsg = (show) => msg.classList.toggle('d-none', !show);

    function validate() {
      const ok = chk.checked && txt.value.trim().toUpperCase() === REQUIRED;
      btn.disabled = !ok;
      showMsg(!ok);
      // mejora accesible (ayuda a lectores de pantalla)
      txt.setAttribute('aria-invalid', String(!ok));
    }

    chk.addEventListener('change', validate);
    txt.addEventListener('input', validate);

    // Evita doble envío y muestra loader si lo tienes
    form.addEventListener('submit', (e) => {
      validate();
      if (btn.disabled) {
        e.preventDefault();
        return;
      }
      btn.disabled = true;
      btn.classList.add('disabled');
      window.AppLoader?.show?.();
    });

    // estado inicial
    validate();

    // opcional: anima tarjetas que usan tu clase utilitaria
    document.querySelectorAll('.animate-on-load').forEach(el => el.classList.add('loaded'));
  });
})();
