// Marca como pasivos los eventos táctiles comunes cuando se registran vía jQuery.
(function () {
  function installPassiveSpecial(type) {
    if (!jQuery.event.special[type]) {
      jQuery.event.special[type] = {};
    }
    const origSetup = jQuery.event.special[type].setup;
    jQuery.event.special[type].setup = function (_, ns, handle) {
      this.addEventListener(type, handle, { passive: true });
      // Evita doble registro si había setup previo
      return false;
    };
  }

  if (window.jQuery) {
    installPassiveSpecial('touchstart');
    installPassiveSpecial('touchmove');
    installPassiveSpecial('wheel');
  }
})();
