document.addEventListener('DOMContentLoaded', function () {
    const loadMoreButton = document.getElementById('cargar-mas-btn');
    const historialItems = document.querySelectorAll('.historial-item');
    let visibleCount = 5; // Inicialmente mostramos 5 citas

    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', function () {
            // Mostrar más citas
            for (let i = visibleCount; i < visibleCount + 5 && i < historialItems.length; i++) {
                historialItems[i].style.display = 'block';
            }
            visibleCount += 5;

            // Si ya no quedan más citas por mostrar, ocultar el botón
            if (visibleCount >= historialItems.length) {
                loadMoreButton.style.display = 'none';
            }
        });
    }
});
