// /static/js/tooltips.js

document.addEventListener("DOMContentLoaded", function() {
    // Hitta alla element som har data-bs-toggle="tooltip"
    const tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
      new bootstrap.Tooltip(tooltipTriggerEl, {
        delay: { show: 0, hide: 100 },  // Visa direkt, göm efter 100 ms
        boundary: "window"
      });
    });
  });
  