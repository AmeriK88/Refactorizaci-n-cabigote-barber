document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("chart-citas");
  if (!canvas) return;

  const endpoint = canvas.dataset.endpoint;
  if (!endpoint) {
    console.error("Falta data-endpoint en #chart-citas");
    return;
  }

  const loadChartJs = async () => {
    if (window.Chart) return;

    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/chart.js";
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };

  const render = async () => {
    try {
      await loadChartJs();

      const res = await fetch(endpoint, { credentials: "same-origin" });
      const data = await res.json();

      const ctx = canvas.getContext("2d");

      // Si recargas o re-renderizas, evita duplicar instancias
      if (canvas._chartInstance) {
        canvas._chartInstance.destroy();
      }

      canvas._chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Citas",
              data: data.counts,
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    } catch (e) {
      console.error("Error cargando gráfico:", e);
      alert("No se pudo cargar el gráfico. Mira la consola.");
    }
  };

  render();
});
