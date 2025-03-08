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

    // Animación del contador con Odometer (o similar)
    const odometerElem = document.getElementById("odometer");
    if (odometerElem) {
        // Lee el valor real que Django inyectó en el HTML y lo recorta de espacios
        const realValue = parseInt(odometerElem.innerText.trim(), 10);
        console.log("Real counter value:", realValue);
        
        // En lugar de reiniciarlo a 0, dejamos el valor actual y solo lo actualizamos (si es necesario)
        // Si quieres un efecto de animación, podrías aplicar alguna transición CSS al número
        setTimeout(() => {
            odometerElem.innerText = realValue;
        }, 500);
    }
});
