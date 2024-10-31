document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');

    const showLoader = () => {
        loader.style.display = 'block';
    };

    const hideLoader = () => {
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
});
