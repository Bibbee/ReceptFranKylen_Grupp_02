// /static/js/loading.js

// Display loading spinner and disable search button when the form is submitted
document.addEventListener('DOMContentLoaded', () => {

    // Select the recipe search form, spinner, and button elements
    const form    = document.querySelector('form[action="/"]');
    const spinner = document.getElementById('loadingSpinner');
    const button  = document.getElementById('searchBtn');
  
    // If any element is missing, do nothing
    if (!form || !spinner || !button) return;
  

    // Attach submit handler to the form
    form.addEventListener('submit', () => {
// Show spinner and disable button
spinner.classList.remove('d-none');
      button.disabled = true;
    });
  });
  