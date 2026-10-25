(() => {
  const root = document.documentElement;
  const supportedThemes = new Set(["light", "dark", "auto"]);
  const select = document.getElementById("cb-admin-theme");
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  let currentTheme = root.dataset.theme || "auto";

  const publishThemeChange = () => {
    const nextTheme = root.dataset.theme || "auto";
    if (!supportedThemes.has(nextTheme) || nextTheme === currentTheme) return;
    currentTheme = nextTheme;
    if (select instanceof HTMLSelectElement) select.value = nextTheme;
    root.dispatchEvent(new Event("cabigote:theme-change"));
  };

  if (select instanceof HTMLSelectElement) {
    select.value = supportedThemes.has(currentTheme) ? currentTheme : "auto";
    select.addEventListener("change", () => {
      const theme = select.value;
      if (!supportedThemes.has(theme)) {
        console.error(`Tema de administrador no válido: ${theme}`);
        select.value = currentTheme;
        return;
      }

      try {
        localStorage.setItem("theme", theme);
      } catch (error) {
        console.error("No se pudo guardar la preferencia de tema.", error);
      }
      root.dataset.theme = theme;
      publishThemeChange();
    });
  }

  new MutationObserver(publishThemeChange).observe(root, {
    attributeFilter: ["data-theme"],
  });

  systemTheme.addEventListener("change", () => {
    if (root.dataset.theme === "auto") {
      root.dispatchEvent(new Event("cabigote:theme-change"));
    }
  });

  window.addEventListener("storage", (event) => {
    if (event.key !== "theme" || !supportedThemes.has(event.newValue)) return;
    root.dataset.theme = event.newValue;
    publishThemeChange();
  });
})();
