// Handle custom diet filter chips and set selected diet for form submission

document.addEventListener("DOMContentLoaded", function () {
  const chipArea = document.getElementById("chip-area");
  const inputField = document.getElementById("ingredients-input");
  const dietInput = document.getElementById("selected-diet"); // ← hidden input to pass selected diet
  const selectedFilters = new Set();

  // Clear the input field initially
  inputField.value = "";

  // When a diet tag is clicked, create a removable chip
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

        // Uncheck corresponding radio button when chip is removed
        document.querySelectorAll('.filter-tags input[type="radio"]').forEach(r => {
          if (r.value.toLowerCase() === value.toLowerCase()) r.checked = false;
        });
      });

      chipArea.appendChild(chip);
    });
  });

  // On form submit, assign selected diet to hidden input
  document.querySelector('.find-recipe-btn').addEventListener('click', () => {
    const ingredients = inputField.value;
    const diets = Array.from(selectedFilters);

    if (dietInput) {
      dietInput.value = diets[0] || ''; // Only one diet allowed by Spoonacular API
    }

    console.log('Submitted form data:', {
      ingredients: ingredients,
      diet: dietInput.value
    });

    // Form submission proceeds normally
  });
});


