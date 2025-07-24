document.addEventListener('DOMContentLoaded', () => {
    const inputFecha = document.querySelector('input[name="fecha"]');
    const inputHora  = document.querySelector('select[name="hora"]');

    // ------------------------------------------------------
    // Helper: formatea con cero a la izquierda (para "HH:MM")
    // ------------------------------------------------------
    const pad = n => String(n).padStart(2, '0');

    // ------------------------------------------------------
    // Function to update (enable/disable) occupied hours
    // ------------------------------------------------------
    const updateOccupiedHours = () => {
        const selectedDate  = inputFecha.value;
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

        // ------------------------------------------------------
        // NEW: disable past hours if the selected date is today
        // ------------------------------------------------------
        const todayISO = new Date().toISOString().split('T')[0];
        if (selectedDate === todayISO) {
            const now        = new Date();
            const horaActual = `${pad(now.getHours())}:${pad(now.getMinutes())}`;

            Array.from(inputHora.options).forEach(option => {
                if (option.value && option.value <= horaActual) {
                    option.disabled = true;
                }
            });
        }
    };

    // ------------------------------------------------------
    // New function: disable hours specified in the blocked hours dictionary
    // ------------------------------------------------------
    const updateBlockedHours = () => {
        const selectedDate    = inputFecha.value;
        // 'bloqueos_por_fecha' should be provided as a JSON object from your backend
        const horasBloqueadas = bloqueos_por_fecha[selectedDate] || [];

        Array.from(inputHora.options).forEach(option => {
            if (horasBloqueadas.includes(option.value)) {
                option.disabled = true;
            }
        });
    };

    if (inputFecha) {
        // ------------------------------------------------------
        // Optional UX: prevent choosing past dates at all
        // ------------------------------------------------------
        const minDateISO = new Date().toISOString().split('T')[0];
        inputFecha.setAttribute('min', minDateISO);

        // Update hours
        updateOccupiedHours();

        const reservedDates = fechasOcupadas.map(fecha   => new Date(fecha).toISOString().split('T')[0]);
        const blockedDates  = fechasBloqueadas.map(fecha => new Date(fecha).toISOString().split('T')[0]);

        // ------------------------------------------------------
        // Listener directo al input (no dentro de 'focus' para evitar duplicados)
        // ------------------------------------------------------
        inputFecha.addEventListener('input', () => {
            const selectedDate = inputFecha.value;
            if (blockedDates.includes(selectedDate)) {
                alert("¡Estás bonito! Te recuerdo que este día no curro niñote.");
                inputFecha.value = '';
            } else if (reservedDates.includes(selectedDate)) {
                alert("¡Chacho loco! La fecha seleccionada está completamente reservada.");
                inputFecha.value = '';
            } else {
                updateOccupiedHours();
            }
        });
    }
});
