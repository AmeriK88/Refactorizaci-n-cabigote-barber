document.addEventListener("DOMContentLoaded", () => {
    // Animación general en elementos con clase .animate-on-load
    const animatedElements = document.querySelectorAll(".animate-on-load");
    animatedElements.forEach((element) => {
        element.style.opacity = "0";
        element.style.transform = "translateY(20px)";

        setTimeout(() => {
            element.style.transition = "opacity 0.5s ease-out, transform 0.5s ease-out";
            element.style.opacity = "1";
            element.style.transform = "translateY(0)";
        }, 100);
    });

    // Animación del contador con Odometer (o simple, si no usas Odometer)
    const odometerElem = document.getElementById("odometer"); 
    if (odometerElem) {
        // Lee el valor real que Django inyectó en el HTML
        const realValue = parseInt(odometerElem.innerText, 10);

        // Opción: arrancar en 0 para que se note la animación
        odometerElem.innerText = 0;

        setTimeout(() => {
            // Cambiamos al valor real, creando el efecto de subida
            odometerElem.innerText = realValue;
        }, 500);
    }
});
