document.addEventListener("DOMContentLoaded", () => {
  const detailsList = document.querySelectorAll("details.details-anim");

  detailsList.forEach((details) => {
    const content = details.querySelector(".details-content");
    if (!content) return;

    // Si viene abierto por defecto, ajusta altura inicial
    if (details.open) {
      content.style.height = "auto";
    }

    details.addEventListener("toggle", () => {
      // Cerrar
      if (!details.open) {
        const start = content.scrollHeight;
        content.style.height = start + "px";      // fija altura actual
        content.offsetHeight;                     // reflow
        content.style.transition = "height 220ms ease";
        content.style.height = "0px";
        return;
      }

      // Abrir
      content.style.transition = "height 220ms ease";
      content.style.height = "0px";
      content.offsetHeight;                       // reflow
      const end = content.scrollHeight;
      content.style.height = end + "px";

      // Al terminar, dejamos auto para que crezca si cambia el contenido
      const onEnd = (e) => {
        if (e.propertyName !== "height") return;
        content.style.height = "auto";
        content.removeEventListener("transitionend", onEnd);
      };
      content.addEventListener("transitionend", onEnd);
    });
  });
});
