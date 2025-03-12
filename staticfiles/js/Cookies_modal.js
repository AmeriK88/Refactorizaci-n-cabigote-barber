$(document).ready(function () {
    const cookiesModal = new bootstrap.Modal(document.getElementById('cookiesModal'));

    // Verificar si el usuario ya ha aceptado o rechazado las cookies
    const cookiesPreference = localStorage.getItem('cookiesPreference');
    if (!cookiesPreference) {
        // Mostrar el modal solo si no hay preferencia almacenada
        cookiesModal.show();
    }

    // Función para manejar el consentimiento de cookies
    function setCookiePreference(preference) {
        localStorage.setItem('cookiesPreference', preference);
        cookiesModal.hide();
        console.log(`Cookies ${preference}.`);
    }

    // Botón "Aceptar"
    $('#cookiesModal .btn-primary').click(function () {
        setCookiePreference('accepted');
    });

    // Botón "Rechazar" y Guardar como rechazado
    $('#cookiesModal .btn-outline-secondary').click(function () {
        setCookiePreference('rejected');
    });

    // Mostrar enlace a la política de privacidad
    $('#privacyPolicyLink').click(function (event) {
        event.preventDefault();
        $('#privacyPolicyModal').modal('show');
    });
});
