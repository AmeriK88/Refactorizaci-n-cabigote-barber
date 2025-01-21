$(document).ready(function() {
    // Visible cuando home está cargado
    $('.hero-content').addClass('visible');

    // Añadir retraso 
    setTimeout(function() {
        $('.hero-image').addClass('visible');
    }, 200); 
});
