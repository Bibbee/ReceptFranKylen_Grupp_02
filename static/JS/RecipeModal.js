// Handle click on recipe images to open a detailed modal with full recipe information
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.recipe-img').forEach(img => {
    img.addEventListener('click', () => {
      document.getElementById('recipeModalLabel').textContent = img.dataset.title;
      document.getElementById('recipeModalImage').src = img.dataset.image;
      document.getElementById('recipeModalDifficulty').textContent = img.dataset.difficulty || 'Unknown';
      document.getElementById('recipeModalTime').textContent = img.dataset.time || 'Unknown';
      document.getElementById('recipeModalServings').textContent = img.dataset.servings || 'Unknown';
      document.getElementById('recipeModalNutrition').textContent = img.dataset.nutrition || 'Information missing';

      const card = img.closest('.card');
      document.getElementById('recipeModalInstructions').innerHTML =
        card.dataset.instructions || '<p>No description available.</p>';

      const modal = new bootstrap.Modal(document.getElementById('recipeModal'));
      modal.show();
    });
  });
});
