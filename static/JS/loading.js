// /static/js/loading.js
document.addEventListener('DOMContentLoaded', () => {
    const form    = document.querySelector('form[action="/"]');
    const spinner = document.getElementById('loadingSpinner');
    const button  = document.getElementById('searchBtn');
  
    if (!form || !spinner || !button) return;
  
    form.addEventListener('submit', () => {
      // Visa spinner och inaktivera knapp
      spinner.classList.remove('d-none');
      button.disabled = true;
    });
  });
  