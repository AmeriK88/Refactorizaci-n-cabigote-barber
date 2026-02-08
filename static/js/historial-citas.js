document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('cargar-mas-btn');
  const items = Array.from(document.querySelectorAll('.historial-item'));
  let visible = 6;

  items.forEach((item, i) => {
    item.style.display = i < visible ? '' : 'none';
  });

  if (btn && items.length <= visible) {
    btn.style.display = 'none';
  }

  if (btn) {
    btn.addEventListener('click', function () {
      for (let i = visible; i < visible + 6 && i < items.length; i++) {
        items[i].style.display = '';
      }
      visible += 6;
      if (visible >= items.length) {
        btn.style.display = 'none';
      }
    });
  }
});
