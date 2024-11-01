document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');
    const overlay = document.getElementById('overlay');
    // Muestra el overlay & // Muestra el loader
    const showLoader = () => {
        overlay.style.display = 'block'; 
        loader.style.display = 'block'; 
    };
    // Oculta el overlay & laoder
    const hideLoader = () => {
        overlay.style.display = 'none'; 
        loader.style.display = 'none'; 
    };

    // Mostrar el loader al enviar un formulario
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            showLoader();
        });
    });

    // Mostrar el loader al hacer clic en un enlace que cargue otra vista
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', event => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('#') && !link.hasAttribute('download')) {
                showLoader();
            }
        });
    });

    // Ocultar el loader cuando la página ha terminado de cargar
    window.addEventListener('load', () => {
        hideLoader();
    });

    // Ocultar el loader y overlay al cargar la página por primera vez
    hideLoader();

    // Ocultar el loader y overlay al volver a la pestaña
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            hideLoader();
        }
    });
});
