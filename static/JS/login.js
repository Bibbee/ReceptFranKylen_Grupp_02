document.addEventListener('DOMContentLoaded', () => {
  console.log("login.js loaded!");
  //const form = document.getElementById('loginForm');
  //if (!form) {
  //  console.log("Formuläret hittades inte!");
  //  return;
  //}

 // console.log("Form hittades! Lägger till event listener...");
 // form.addEventListener('submit', async e => {
 //   e.preventDefault();
 //   console.log("Inloggningsförsök skickas...");

 //   const formData = new FormData(form);
 //   const res = await fetch('/login', {
 //     method: 'POST',
 //     headers: { 'X-Requested-With': 'XMLHttpRequest' },
 //     body: formData,
 //     credentials: 'include'
 //   });

 //   const json = await res.json();
 //   console.log("Svar från server:", json);

 //   if (json.ok) {
 //     console.log("Login lyckades, redirectar till /favorites");
 //     console.log("Cookies före redirect:", document.cookie);

 //     bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
 //     window.location.href = "/favorites";
 //   } else {
 //     const err = document.getElementById('loginError');
 //     err.textContent = json.error;
 //     err.classList.remove('d-none');
 //   }
 // });
}); 
