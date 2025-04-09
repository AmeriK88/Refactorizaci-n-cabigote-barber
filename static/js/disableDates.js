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
        // Call the function to update occupied hours on initial load
        updateOccupiedHours();

        inputFecha.addEventListener('focus', () => {
            const reservedDates = fechasOcupadas.map(fecha => new Date(fecha).toISOString().split('T')[0]);
            const blockedDates = fechasBloqueadas.map(fecha => new Date(fecha).toISOString().split('T')[0]);

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
        });
    }
});
