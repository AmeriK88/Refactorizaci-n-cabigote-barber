$(document).ready(function() {
    // Mostrar el modal de cookies si el usuario no ha aceptado ni rechazado
    if (!localStorage.getItem('cookiesAccepted') && !localStorage.getItem('cookiesRejected')) {
        var cookiesModal = new bootstrap.Modal(document.getElementById('cookiesModal'));
        cookiesModal.show();
    }

    // Función para manejar la aceptación o rechazo de cookies
    function handleCookieConsent(action) {
        localStorage.setItem(action, 'true');
        var cookiesModal = bootstrap.Modal.getInstance(document.getElementById('cookiesModal'));
        if (cookiesModal) {
            cookiesModal.hide();
        }
        console.log(`Cookies ${action === 'cookiesAccepted' ? 'accepted' : 'rejected'}.`);
    }

    $('#cookiesModal .btn-primary').click(function() {
        handleCookieConsent('cookiesAccepted');
    });

    $('#cookiesModal .btn-secondary').click(function() {
        handleCookieConsent('cookiesRejected');
    });

    $('#cookiesPolicyLink').click(function(event) {
        event.preventDefault(); 
        $('#cookiesModal').modal('show'); 
    });

    $('#privacyPolicyLink').click(function(event) {
        event.preventDefault(); 
        $('#privacyPolicyModal').modal('show'); 
    });
});
