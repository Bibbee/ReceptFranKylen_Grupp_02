// Handle clicks on favorite star buttons to save a recipe to the user's favorites

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.favorite-star').forEach(button => {
    button.addEventListener('click', async () => {
      const recipeId = button.dataset.recipeId;
      const title = button.dataset.title;
      const image = button.dataset.image;
      const difficulty = button.dataset.difficulty || 'Unknown';
      const time = button.dataset.time || 'Unknown';
      const servings = button.dataset.servings || 'Unknown';
      const nutrition = button.dataset.nutrition || 'Information missing';
      const instructions = button.dataset.instructions || 'No instructions available.';
      const ingredients  = button.dataset.ingredients;

      const formData = new FormData();
      formData.append('recipe_id', recipeId);
      formData.append('title', title);
      formData.append('image', image);
      formData.append('difficulty', difficulty);
      formData.append('ready_in_minutes', time);
      formData.append('servings', servings);
      formData.append('nutrition', nutrition);
      formData.append('instructions', instructions);
      formData.append('ingredients', ingredients);

      try {
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
          alert('Something went wrong: ' + res.status);
        }
      } catch (error) {
        console.error('Error saving favorite:', error);
        alert('A network error occurred.');
      }
    });
  });
});
