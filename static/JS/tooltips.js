// /static/js/tooltips.js



 //Initializes Bootstrap tooltips on elements with data-bs-toggle="tooltip" 
 //so that tooltips appear immediately on hover and hide after a short delay.



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
  