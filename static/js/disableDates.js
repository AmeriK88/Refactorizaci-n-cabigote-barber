document.addEventListener("DOMContentLoaded", () => {
  const inputFecha = document.querySelector('input[name="fecha"]');
  const inputHora = document.querySelector('select[name="hora"]');
  const inputServicio = document.querySelector('select[name="servicio"]');

  // Si no existen los inputs, salimos
  if (!inputFecha || !inputHora) return;

  // ---------- Helpers ----------
  const pad = (n) => String(n).padStart(2, "0");
  const normalizeTime = (v) => (v || "").trim().slice(0, 5); // "10:00:00" -> "10:00"

  const safeJSON = (id, fallback) => {
    const el = document.getElementById(id);
    if (!el) return fallback;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      console.error(`JSON inválido en #${id}`, e);
      return fallback;
    }
  };

  const hasAnyEnabledHour = () => {
    return Array.from(inputHora.options).some(
      (opt) => opt.value && !opt.disabled
    );
  };

  // ---------- Data desde Django ----------
  const fechasOcupadas = safeJSON("fechas-ocupadas", []);
  const fechasBloqueadas = safeJSON("fechas-bloqueadas", []);
  const horasOcupadasPorFecha = safeJSON("horas-ocupadas-por-fecha", {});
  const bloqueosPorFecha = safeJSON("bloqueos-por-fecha", {});
  const unavailableByService = safeJSON("unavailable-by-service", {});

  // ---------- Normaliza fechas a ISO ----------
  const reservedDates = fechasOcupadas.map((f) => String(f).slice(0, 10));
  const blockedDates = fechasBloqueadas.map((f) => String(f).slice(0, 10));

  // Evitar fechas pasadas
  const minDateISO = new Date().toISOString().split("T")[0];
  inputFecha.setAttribute("min", minDateISO);

  // ---------- Lógica ----------
  const getHorasSolapadas = (selectedDate) => {
    if (!selectedDate || !inputServicio?.value) return [];
    return unavailableByService[inputServicio.value]?.[selectedDate] || [];
  };

  const enableAllHourOptions = () => {
    Array.from(inputHora.options).forEach((option) => {
      if (!option.value) return;
      option.disabled = false;
    });
  };

  const disableHoursList = (hoursList) => {
    const set = new Set((hoursList || []).map(normalizeTime));
    Array.from(inputHora.options).forEach((option) => {
      const opt = normalizeTime(option.value);
      if (opt && set.has(opt)) option.disabled = true;
    });
  };

  const disableBlockedHours = (selectedDate) => {
    disableHoursList(bloqueosPorFecha[selectedDate] || []);
  };

  const disablePastHoursIfToday = (selectedDate) => {
    const todayISO = new Date().toISOString().split("T")[0];
    if (selectedDate !== todayISO) return;

    const now = new Date();
    const horaActual = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

    Array.from(inputHora.options).forEach((option) => {
      const opt = normalizeTime(option.value);
      if (opt && opt <= horaActual) option.disabled = true;
    });
  };

  const updateHours = () => {
    const selectedDate = inputFecha.value;
    if (!selectedDate) return;

    // 1) Reset
    enableAllHourOptions();

    // 2) Horas ya ocupadas
    disableHoursList(horasOcupadasPorFecha[selectedDate] || []);

    // 3) Solapes por duración del servicio
    disableHoursList(getHorasSolapadas(selectedDate));

    // 4) Bloqueos del admin
    disableBlockedHours(selectedDate);

    // 5) Horas pasadas si es hoy
    disablePastHoursIfToday(selectedDate);

    // 6) 🔥 FIX CLAVE: día sin ninguna hora disponible
    if (!hasAnyEnabledHour()) {
      alert(
        "Mi niño, este día ya no tiene hueco ni pa’ colar un café ☕. Elige otro."
      );
      inputFecha.value = "";
      enableAllHourOptions();
    }
  };

  // ---------- Eventos ----------
  if (inputFecha.value) updateHours();

  inputFecha.addEventListener("input", () => {
    const selectedDate = inputFecha.value;
    if (!selectedDate) return;

    if (blockedDates.includes(selectedDate)) {
      alert("Ese día no curro, máquina. Está bloqueado.");
      inputFecha.value = "";
      enableAllHourOptions();
      return;
    }

    if (reservedDates.includes(selectedDate)) {
      alert("Ese día está completo completo, niñote.");
      inputFecha.value = "";
      enableAllHourOptions();
      return;
    }

    updateHours();
  });

  if (inputServicio) {
    inputServicio.addEventListener("change", updateHours);
  }
});
