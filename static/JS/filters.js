document.addEventListener("DOMContentLoaded", function () {
  const chipArea = document.getElementById("chip-area");
  const inputField = document.getElementById("ingredients-input");
  const dietInput = document.getElementById("selected-diet"); // ← lägg till hidden input i HTML
  const selectedFilters = new Set();

  inputField.value = "";

  document.querySelectorAll('.filter-tags span').forEach(tag => {
    tag.addEventListener('click', () => {
      const value = tag.dataset.text;

      if (selectedFilters.has(value.toLowerCase())) return;

      selectedFilters.add(value.toLowerCase());

      const chip = document.createElement("div");
      chip.className = "chip";
      chip.innerHTML = `${value} <button class="remove-chip" title="Remove">×</button>`;

      chip.querySelector(".remove-chip").addEventListener("click", () => {
        chip.remove();
        selectedFilters.delete(value.toLowerCase());

        document.querySelectorAll('.filter-tags input[type="radio"]').forEach(r => {
          if (r.value.toLowerCase() === value.toLowerCase()) r.checked = false;
        });
      });

      chipArea.appendChild(chip);
    });
  });

  document.querySelector('.find-recipe-btn').addEventListener('click', () => {
    const ingredients = inputField.value;
    const diets = Array.from(selectedFilters);

    if (dietInput) {
      dietInput.value = diets[0] || ''; // Spoonacular tillåter endast en diet
    }

    console.log('Formdata som skickas:', {
      ingredients: ingredients,
      diet: dietInput.value
    });

    // formuläret skickas automatiskt (ingen preventDefault behövs)
  });
});
