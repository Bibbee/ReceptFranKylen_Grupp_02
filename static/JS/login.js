// static/js/login.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    if (!form) return;
  
    form.addEventListener('submit', async e => {
      e.preventDefault();
  
      const formData = new FormData(form);
      const res = await fetch('/login', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      });
  
      const json = await res.json();
      if (json.ok) {
        // Stäng Bootstrap-modal
        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
        // Redirect för att visa lyckat-meddelande
        window.location.href = '/?login=1';
      } else {
        const err = document.getElementById('loginError');
        err.textContent = json.error;
        err.classList.remove('d-none');
      }
    });
  });
  