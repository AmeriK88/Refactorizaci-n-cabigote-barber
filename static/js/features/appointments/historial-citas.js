document.addEventListener('DOMContentLoaded', function () {
  const btn   = document.getElementById('cargar-mas-btn');
  const items = Array.from(document.querySelectorAll('.historial-item'));
  let visible = 5;

  // 1) Oculta todo lo que vaya más allá del quinto
  items.forEach((item, i) => {
    item.style.display = i < visible ? '' : 'none';
  });

  // 2) Si no hay más de 5, quita el botón
  if (btn && items.length <= visible) {
    btn.style.display = 'none';
  }

  // 3) Al click, muestra los siguientes 5 y actualiza contador
  if (btn) {
    btn.addEventListener('click', function () {
      for (let i = visible; i < visible + 5 && i < items.length; i++) {
        items[i].style.display = '';
      }
      visible += 5;
      if (visible >= items.length) {
        btn.style.display = 'none';
      }
    });
  }
});
