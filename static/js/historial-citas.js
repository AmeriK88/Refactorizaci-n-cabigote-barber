document.addEventListener("DOMContentLoaded", () => {
  // =========================
  // 1) Animación de <details>
  // =========================
  const detailsList = document.querySelectorAll("details.details-anim");

  detailsList.forEach((details) => {
    const content = details.querySelector(".card-body");
    if (!content) return;

    // Initial state
    content.style.overflow = "hidden";
    content.style.height = details.open ? "auto" : "0px";

    details.addEventListener("toggle", () => {
      // CXL transitions
      content.style.transition = "height 220ms ease";

      if (details.open) {
        // OPEN: 0 -> scrollHeight -> auto
        content.style.height = "0px";
        content.offsetHeight;
        content.style.height = content.scrollHeight + "px";

        const onEnd = (e) => {
          if (e.propertyName !== "height") return;
          content.style.height = "auto";
          content.removeEventListener("transitionend", onEnd);
        };
        content.addEventListener("transitionend", onEnd);

      } else {
        // CLOSE: auto/actual -> 0
        content.style.height = content.scrollHeight + "px";
        content.offsetHeight; 
        content.style.height = "0px";
      }
    });
  });

  // ==========================================
  // 2) HISTORY: 5 months + "Load +"
  // ==========================================
  const meses = Array.from(document.querySelectorAll("details.historial-mes"));
  const btn = document.getElementById("cargar-mas-btn");
  if (!btn) return;

  const BATCH = 5;

  if (meses.length <= BATCH) {
    btn.style.display = "none";
    return;
  }

  let visible = BATCH;
  meses.forEach((m, i) => {
    if (i >= BATCH) m.style.display = "none";
  });

  btn.style.display = "inline-block";

  btn.addEventListener("click", () => {
    const next = Math.min(visible + BATCH, meses.length);
    for (let i = visible; i < next; i++) meses[i].style.display = "";
    visible = next;
    if (visible >= meses.length) btn.style.display = "none";
  });
});
