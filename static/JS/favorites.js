document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.favorite-star').forEach(button => {
      button.addEventListener('click', async () => {
        const recipeId = button.dataset.recipeId;
        const title = button.dataset.title;
        const image = button.dataset.image;
        const difficulty = button.dataset.difficulty || 'Okänd';
        const time = button.dataset.time || 'Okänt';
        const servings = button.dataset.servings || 'Okänt';
        const nutrition = button.dataset.nutrition || 'Information saknas';
        const instructions = button.dataset.instructions || 'Instruktioner saknas.';
  
        const formData = new FormData();
        formData.append('recipe_id', recipeId);
        formData.append('title', title);
        formData.append('image', image);
        formData.append('difficulty', difficulty);
        formData.append('ready_in_minutes', time);
        formData.append('servings', servings);
        formData.append('nutrition', nutrition);
        formData.append('instructions', instructions);

        const res = await fetch('/favorite', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });
  
        if (res.ok) {
            const data = await res.json();
  
        if (data.ok) {
        const toast = new bootstrap.Toast(document.getElementById('toastSaved'));
        toast.show();
        } else {
        const toast = new bootstrap.Toast(document.getElementById('toastExists'));
        toast.show();
     }
        } else {
          alert('Något gick fel: ' + res.status);
        }
      });
    });
  });
  
  