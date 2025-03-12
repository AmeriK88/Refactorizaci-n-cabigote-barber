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
});
