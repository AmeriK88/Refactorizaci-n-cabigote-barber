document.addEventListener("DOMContentLoaded", () => {
    const animatedElements = document.querySelectorAll(".animate-on-load");

    animatedElements.forEach((element) => {
        element.style.opacity = "0"; // Ocultar inicialmente
        element.style.transform = "translateY(20px)"; // Desplazar ligeramente

        // Agregar un retraso para la animación
        setTimeout(() => {
            element.style.transition = "opacity 0.5s ease-out, transform 0.5s ease-out";
            element.style.opacity = "1"; // Mostrar
            element.style.transform = "translateY(0)"; // Volver a su posición
        }, 100); // Retraso de inicio en milisegundos
    });
});
