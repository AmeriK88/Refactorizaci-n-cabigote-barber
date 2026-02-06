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

  // ---------- Data desde Django (json_script) ----------
  const fechasOcupadas = safeJSON("fechas-ocupadas", []);
  const fechasBloqueadas = safeJSON("fechas-bloqueadas", []);
  const horasOcupadasPorFecha = safeJSON("horas-ocupadas-por-fecha", {});
  const bloqueosPorFecha = safeJSON("bloqueos-por-fecha", {});
  const unavailableByService = safeJSON("unavailable-by-service", {});

  // ---------- Normaliza fechas a ISO "YYYY-MM-DD" ----------
  const reservedDates = (fechasOcupadas || []).map((f) => {
    // si viene "2026-02-05" perfecto
    // si viene Date/otro formato, intenta convertir
    try {
      return new Date(f).toISOString().split("T")[0];
    } catch {
      return String(f).slice(0, 10);
    }
  });

  const blockedDates = (fechasBloqueadas || []).map((f) => {
    try {
      return new Date(f).toISOString().split("T")[0];
    } catch {
      return String(f).slice(0, 10);
    }
  });

  // Evitar elegir fechas pasadas
  const minDateISO = new Date().toISOString().split("T")[0];
  inputFecha.setAttribute("min", minDateISO);

  // ---------- Lógica ----------
  const getHorasSolapadas = (selectedDate) => {
    if (!selectedDate) return [];
    const serviceId = inputServicio ? inputServicio.value : null;
    if (!serviceId) return [];
    const mapForService = unavailableByService[String(serviceId)] || {};
    return mapForService[selectedDate] || [];
  };

  const enableAllHourOptions = () => {
    Array.from(inputHora.options).forEach((option) => {
      if (!option.value) return; // placeholder
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
    const horasBloqueadas = bloqueosPorFecha[selectedDate] || [];
    disableHoursList(horasBloqueadas);
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

    // 2) Occupied (por fecha)
    const ocupadas = horasOcupadasPorFecha[selectedDate] || [];
    disableHoursList(ocupadas);

    // 3) Overlaps (por servicio y fecha)
    const solapadas = getHorasSolapadas(selectedDate);
    disableHoursList(solapadas);

    // 4) Blocked (por rangos)
    disableBlockedHours(selectedDate);

    // 5) Past hours today
    disablePastHoursIfToday(selectedDate);
  };

  // ---------- Eventos ----------
  // Si ya hay fecha precargada
  if (inputFecha.value) updateHours();

  // Cuando cambias fecha
  inputFecha.addEventListener("input", () => {
    const selectedDate = inputFecha.value;
    if (!selectedDate) return;

    if (blockedDates.includes(selectedDate)) {
      alert("¡Estás bonito! Te recuerdo que este día no curro niñote.");
      inputFecha.value = "";
      enableAllHourOptions();
      return;
    }

    if (reservedDates.includes(selectedDate)) {
      alert("¡Chacho loco! La fecha seleccionada está completamente reservada.");
      inputFecha.value = "";
      enableAllHourOptions();
      return;
    }

    updateHours();
  });

  // Cuando cambias servicio, recalcula solapes
  if (inputServicio) {
    inputServicio.addEventListener("change", () => {
      updateHours();
    });
  }
});
