// static/js/special_message.js

document.addEventListener('DOMContentLoaded', () => {
  const modalElement = document.getElementById('specialMessageModal');
  if (modalElement) {
      const messageId = modalElement.getAttribute('data-message-id');
      console.log('Mensaje ID:', messageId);  // Depuración

      // Obtener la lista de mensajes ya mostrados de localStorage
      let shownMessages = JSON.parse(localStorage.getItem('shownMessages')) || [];
      console.log('Mensajes mostrados:', shownMessages);  // Depuración

      if (!shownMessages.includes(messageId)) {
          // Crear la instancia del modal
          const bsModal = new bootstrap.Modal(modalElement, {
              backdrop: true,    // Permite cerrar el modal haciendo clic fuera
              keyboard: true,    // Permite cerrar el modal con la tecla ESC
              focus: true        // Enfoca el modal cuando se abre
          });
          bsModal.show();
          console.log('Mostrando modal para el mensaje ID:', messageId);  // Depuración

          // Añadir el ID del mensaje a la lista de mostrados
          shownMessages.push(messageId);
          localStorage.setItem('shownMessages', JSON.stringify(shownMessages));
          console.log('Actualizando shownMessages:', shownMessages);  // Depuración
      } else {
          console.log('El mensaje ya ha sido mostrado anteriormente.');
      }
  }
});
