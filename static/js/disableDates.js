document.addEventListener('DOMContentLoaded', () => {
    const inputFecha = document.querySelector('input[name="fecha"]');
    const inputHora = document.querySelector('select[name="hora"]');

    // Function to update (enable/disable) occupied hours
    const updateOccupiedHours = () => {
        const selectedDate = inputFecha.value;
        const horasOcupadas = horasOcupadasPorFecha[selectedDate] || [];

        // First, enable all options
        Array.from(inputHora.options).forEach(option => {
            option.disabled = false;
        });

        // Disable the hours that are occupied
        horasOcupadas.forEach(hora => {
            Array.from(inputHora.options).forEach(option => {
                if (option.value === hora) {
                    option.disabled = true;
                }
            });
        });

        // Also disable blocked hours
        updateBlockedHours();
    };

    // New function: disable hours specified in the blocked hours dictionary
    const updateBlockedHours = () => {
        const selectedDate = inputFecha.value;
        // 'bloqueos_por_fecha' should be provided as a JSON object from your backend
        const horasBloqueadas = bloqueos_por_fecha[selectedDate] || [];

        Array.from(inputHora.options).forEach(option => {
            if (horasBloqueadas.includes(option.value)) {
                option.disabled = true;
            }
        });
    };

    if (inputFecha) {
      
    // 1) Llama una vez al cargar
    // ──────────────────────────────────────────────────────────
    updateOccupiedHours();

    // ──────────────────────────────────────────────────────────
    // 2) Listener: al enfocar el campo fecha
    // ──────────────────────────────────────────────────────────
    inputFecha.addEventListener('focus', () => {
    // Normalizamos listas a YYYY‑MM‑DD
    const reservedDates = fechasOcupadas.map(
        f => new Date(f).toISOString().split('T')[0]
    );
    const blockedDates = fechasBloqueadas.map(
        f => new Date(f).toISOString().split('T')[0]
    );

    // ───── Listener interno: cada vez que cambia la fecha ─────
    inputFecha.addEventListener('input', () => {
        const selectedDate = inputFecha.value;

        if (blockedDates.includes(selectedDate)) {
        alert("¡Estás bonito! Te recuerdo que este día no curro niñote.");
        inputFecha.value = '';
        return;
        }

        if (reservedDates.includes(selectedDate)) {
        alert("¡Chacho loco! La fecha seleccionada está completamente reservada.");
        inputFecha.value = '';
        return;
        }

        // Fecha válida → actualizamos horas
        updateOccupiedHours();

        /* ────────────────────────────────────────────────
        3) Si la fecha es hoy, deshabilita horas pasadas
        ──────────────────────────────────────────────── */
        const hoyISO = new Date().toISOString().split('T')[0];

        if (selectedDate === hoyISO) {
        const ahora = new Date();

        Array.from(inputHora.options).forEach(opt => {
            if (!opt.value) return;            
            const [h, m] = opt.value.split(':').map(Number);
            const optDate = new Date();
            optDate.setHours(h, m, 0, 0);

            // Desactiva si la hora ya ocurrió
            if (optDate <= ahora) opt.disabled = true;
            });
          }
        });
      });   
    }  
  });         