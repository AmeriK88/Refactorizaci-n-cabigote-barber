document.addEventListener("DOMContentLoaded", () => {
  const inputFecha = document.querySelector('input[name="fecha"]');
  const inputHora = document.querySelector('select[name="hora"]');
  const inputServicio = document.querySelector('select[name="servicio"]');

  if (!inputFecha || !inputHora) return;

  const pad = (n) => String(n).padStart(2, "0");
  const normalizeTime = (v) => (v || "").trim().slice(0, 5);

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

  const hasAnyEnabledHour = () =>
    Array.from(inputHora.options).some((opt) => opt.value && !opt.disabled);

  // Data desde Django
  const fechasOcupadas = safeJSON("fechas-ocupadas", []);
  const fechasBloqueadas = safeJSON("fechas-bloqueadas", []);
  const horasOcupadasPorFecha = safeJSON("horas-ocupadas-por-fecha", {});
  const bloqueosPorFecha = safeJSON("bloqueos-por-fecha", {});

  // Normaliza fechas a ISO
  const reservedDates = fechasOcupadas.map((f) => String(f).slice(0, 10));
  const blockedDates = fechasBloqueadas.map((f) => String(f).slice(0, 10));

  // Evitar fechas pasadas
  const minDateISO = new Date().toISOString().split("T")[0];
  inputFecha.setAttribute("min", minDateISO);

  // ===== AJAX availability =====
  const AV_URL = window.AVAILABILITY_URL; // lo defines en el template
  const EXCLUDE_ID = window.EXCLUDE_CITA_ID; // solo en editar
  const cache = new Map(); // key: serviceId|date

  const fetchSolapes = async (serviceId, dateISO) => {
    if (!AV_URL || !serviceId || !dateISO) return [];

    const key = `${serviceId}|${dateISO}|${EXCLUDE_ID || ""}`;
    if (cache.has(key)) return cache.get(key);

    const params = new URLSearchParams({
      service_id: serviceId,
      date: dateISO,
    });

    if (EXCLUDE_ID) params.set("exclude_cita_id", String(EXCLUDE_ID));

    try {
      const res = await fetch(`${AV_URL}?${params.toString()}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!res.ok) return [];
      const data = await res.json();
      const list = Array.isArray(data.unavailable) ? data.unavailable : [];
      cache.set(key, list);
      return list;
    } catch (e) {
      console.error("Error fetch availability", e);
      return [];
    }
  };

  // Helpers options
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

  // ===== Update hours (async) =====
  const updateHours = async () => {
    const selectedDate = inputFecha.value;
    const serviceId = inputServicio?.value;

    if (!selectedDate) return;

    // 1) Reset
    enableAllHourOptions();

    // 2) Horas ya ocupadas
    disableHoursList(horasOcupadasPorFecha[selectedDate] || []);

    // 3) Solapes por duración del servicio (AJAX)
    if (serviceId) {
      const solapes = await fetchSolapes(serviceId, selectedDate);
      disableHoursList(solapes);
    }

    // 4) Bloqueos del admin
    disableBlockedHours(selectedDate);

    // 5) Horas pasadas si es hoy
    disablePastHoursIfToday(selectedDate);

    // 6) Día sin ninguna hora disponible
    if (!hasAnyEnabledHour()) {
      alert("Mi niño, este día ya no tiene hueco ni pa’ colar un café ☕. Elige otro.");
      inputFecha.value = "";
      enableAllHourOptions();
    }
  };

  // Eventos
  if (inputFecha.value) updateHours();

  inputFecha.addEventListener("input", async () => {
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

    await updateHours();
  });

  if (inputServicio) {
    inputServicio.addEventListener("change", async () => {
      if (inputFecha.value) await updateHours();
    });
  }
});
