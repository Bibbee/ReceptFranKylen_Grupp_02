document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.save-recipe-btn').forEach(button => {
      button.addEventListener('click', async () => {
        const recipeId = button.dataset.recipeId;
        const title = button.dataset.title;
        const image = button.dataset.image;
  
        const formData = new FormData();
        formData.append('recipe_id', recipeId);
        formData.append('title', title);
        formData.append('image', image);
  
        const res = await fetch('/favorite', {
          method: 'POST',
          body: formData,
          credentials: 'same-origin'
        });
  
        if (res.ok) {
          const data = await res.json();
          if (data.ok) {
            alert('Receptet sparades via AJAX!');
          } else {
            alert('Server svarade men inte OK.');
          }
        } else {
          alert('Något gick fel: ' + res.status);
        }
      });
    });
  });
  