document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("chart-citas");
  if (!canvas) return;

  const chartWrap = document.getElementById("chart-citas-wrap");
  const loadingMessage = document.getElementById("chart-citas-loading");
  const errorMessage = document.getElementById("chart-citas-error");
  const endpoint = canvas.dataset.endpoint;

  const loadChartJs = async () => {
    if (window.Chart) return;

    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/chart.js";
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };

  const getThemeColors = () => {
    const styles = getComputedStyle(document.documentElement);
    return {
      text: styles.getPropertyValue("--cb-chart-text").trim(),
      grid: styles.getPropertyValue("--cb-chart-grid").trim(),
      bar: styles.getPropertyValue("--cb-chart-bar").trim(),
      border: styles.getPropertyValue("--cb-chart-bar-border").trim(),
      tooltip: styles.getPropertyValue("--cb-chart-tooltip").trim(),
    };
  };

  const showError = (error) => {
    console.error("No se pudo cargar el gráfico de citas.", error);
    if (chartWrap) {
      chartWrap.classList.remove("is-loading");
      chartWrap.setAttribute("aria-busy", "false");
    }
    if (loadingMessage) loadingMessage.hidden = true;
    if (errorMessage) errorMessage.hidden = false;
    canvas.hidden = true;
  };

  if (!endpoint) {
    showError(new Error("Falta data-endpoint en #chart-citas."));
    return;
  }

  const render = async () => {
    try {
      await loadChartJs();

      const response = await fetch(endpoint, { credentials: "same-origin" });
      if (!response.ok) {
        throw new Error(`La API de citas respondió con HTTP ${response.status}.`);
      }
      const data = await response.json();
      if (!Array.isArray(data.labels) || !Array.isArray(data.counts)) {
        throw new Error("La respuesta del gráfico no contiene series válidas.");
      }

      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("No se pudo inicializar el lienzo del gráfico.");

      if (canvas._chartInstance) {
        canvas._chartInstance.destroy();
      }

      const colors = getThemeColors();
      const chart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Citas",
              data: data.counts,
              borderWidth: 1,
              backgroundColor: colors.bar,
              borderColor: colors.border,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: colors.text } },
            tooltip: {
              backgroundColor: colors.tooltip,
              titleColor: colors.text,
              bodyColor: colors.text,
              borderColor: colors.grid,
              borderWidth: 1,
            },
          },
          scales: {
            x: {
              ticks: { color: colors.text },
              grid: { color: colors.grid },
            },
            y: {
              beginAtZero: true,
              ticks: { color: colors.text },
              grid: { color: colors.grid },
            },
          },
        },
      });
      canvas._chartInstance = chart;

      const updateTheme = () => {
        const nextColors = getThemeColors();
        chart.data.datasets[0].backgroundColor = nextColors.bar;
        chart.data.datasets[0].borderColor = nextColors.border;
        chart.options.plugins.legend.labels.color = nextColors.text;
        chart.options.plugins.tooltip.backgroundColor = nextColors.tooltip;
        chart.options.plugins.tooltip.titleColor = nextColors.text;
        chart.options.plugins.tooltip.bodyColor = nextColors.text;
        chart.options.plugins.tooltip.borderColor = nextColors.grid;
        chart.options.scales.x.ticks.color = nextColors.text;
        chart.options.scales.x.grid.color = nextColors.grid;
        chart.options.scales.y.ticks.color = nextColors.text;
        chart.options.scales.y.grid.color = nextColors.grid;
        chart.update("none");
      };

      document.documentElement.addEventListener("cabigote:theme-change", updateTheme);

      if (chartWrap) {
        chartWrap.classList.remove("is-loading");
        chartWrap.setAttribute("aria-busy", "false");
      }
      if (loadingMessage) loadingMessage.hidden = true;
    } catch (error) {
      showError(error);
    }
  };

  render();
});
