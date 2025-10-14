// Toggle de contraseña accesible y reutilizable
document.addEventListener('DOMContentLoaded', () => {
  // Soporta múltiples toggles si los hubiera
  document.querySelectorAll('[data-toggle="password"]').forEach(btn => {
    const targetId = btn.getAttribute('data-target');
    if (!targetId) return;

    const input = document.getElementById(targetId);
    if (!input) return;

    btn.addEventListener('click', () => {
      const showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';

      // icono
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = showing ? 'bi bi-eye' : 'bi bi-eye-slash';
      }

      // aria
      btn.setAttribute('aria-pressed', String(!showing));
    });

    // Acceso con teclado (Enter/Espacio ya funcionan al ser <button>)
  });
});
