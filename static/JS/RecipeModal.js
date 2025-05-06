<<<<<<< Updated upstream
<<<<<<< Updated upstream
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.recipe-img').forEach(img => {
      img.addEventListener('click', () => {
        document.getElementById('recipeModalLabel').textContent = img.dataset.title;
        document.getElementById('recipeModalImage').src = img.dataset.image;
        document.getElementById('recipeModalDifficulty').textContent = img.dataset.difficulty || 'Okänd';
        document.getElementById('recipeModalTime').textContent = img.dataset.time || 'Okänt';
        document.getElementById('recipeModalServings').textContent = img.dataset.servings || 'Okänt';
        document.getElementById('recipeModalNutrition').textContent = img.dataset.nutrition || 'Information saknas';
  
        // 🟢 Hämta instruktionerna från kortets data-attribut (med HTML-lista)
        const card = img.closest('.card');
        document.getElementById('recipeModalInstructions').innerHTML =
          card.dataset.instructions || '<p>Ingen beskrivning tillgänglig</p>';
  
        const modal = new bootstrap.Modal(document.getElementById('recipeModal'));
        modal.show();
      });
    });
  });
  
  
  
=======
=======
>>>>>>> Stashed changes
<script>
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.recipe-img').forEach(img => {
    img.addEventListener('click', () => {
      document.getElementById('recipeModalLabel').textContent = img.dataset.title;
      document.getElementById('recipeModalImage').src = img.dataset.image;
      document.getElementById('recipeModalDifficulty').textContent = img.dataset.difficulty || 'Okänd';
      document.getElementById('recipeModalTime').textContent = img.dataset.time || 'Okänd';
      document.getElementById('recipeModalServings').textContent = img.dataset.servings || 'Okänt';
      document.getElementById('recipeModalNutrition').textContent = img.dataset.nutrition || 'Information saknas';

      const modal = new bootstrap.Modal(document.getElementById('recipeModal'));
      modal.show();
    });
  });
});
</script>
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
