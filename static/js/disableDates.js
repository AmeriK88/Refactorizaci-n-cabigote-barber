document.addEventListener('DOMContentLoaded', () => {
    const inputFecha = document.querySelector('input[name="fecha"]');
    const inputHora = document.querySelector('select[name="hora"]');

    // Función para deshabilitar horas ocupadas
    const updateOccupiedHours = () => {
        const selectedDate = inputFecha.value;
        const horasOcupadas = horasOcupadasPorFecha[selectedDate] || [];

        Array.from(inputHora.options).forEach(option => {
            option.disabled = false; 
        });

        // Deshabilitar las horas ocupadas
        horasOcupadas.forEach(hora => {
            Array.from(inputHora.options).forEach(option => {
                if (option.value === hora) {
                    option.disabled = true;
                }
            });
        });
    };

    if (inputFecha) {
        // Llamar a la función para deshabilitar horas en la carga inicial
        updateOccupiedHours();

        inputFecha.addEventListener('focus', () => {
            const disabledDates = fechasOcupadas.map(fecha => new Date(fecha).toISOString().split('T')[0]);

            inputFecha.addEventListener('input', () => {
                const selectedDate = inputFecha.value;

                if (disabledDates.includes(selectedDate)) {
                    alert("La fecha seleccionada está completamente reservada. Por favor, selecciona otra.");
                    inputFecha.value = '';
                } else {
                    updateOccupiedHours();
                }
            });
        });
    }
});
