// filters.js
// Handles diet tags, filter application, and reliable filter submission

document.addEventListener("DOMContentLoaded", () => {
  // DOM elements
  const form             = document.querySelector('form');
  const ingredientsInput = document.getElementById('ingredients-input');
  const dietInput        = document.getElementById('selected-diet');
  const calSlider        = document.getElementById('max_calories');
  const timeSlider       = document.getElementById('max_time');
  const diffSelect       = document.getElementById('difficulty');
  const applyBtn         = document.getElementById('apply-filters-btn');
  const filterPanelEl    = document.getElementById('filterPanel');
  const chipArea         = document.getElementById('chip-area');

  // State
  let filtersApplied = false;
  const selectedDiet = new Set();

  // Create hidden inputs for reliable submission
  function createHidden(name) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    form.appendChild(input);
    return input;
  }
  const hiddenMaxCalories = createHidden('max_calories');
  const hiddenMaxTime     = createHidden('max_time');
  const hiddenDifficulty  = createHidden('difficulty');

  // Initialize Bootstrap Collapse for filter panel
  const bsCollapse = new bootstrap.Collapse(filterPanelEl, { toggle: false });

  // Add click-outside handler to close the filter panel
  document.addEventListener("click", (e) => {
    // if panel is open and click is neither inside panel nor on the apply button → hide
    if (
      filterPanelEl.classList.contains("show") &&
      !filterPanelEl.contains(e.target) &&
      !applyBtn.contains(e.target)
    ) {
      bsCollapse.hide();
    }
  });

  // Add close button to top-right of panel
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.setAttribute('aria-label', 'Close filter panel');
  closeBtn.addEventListener('click', () => bsCollapse.hide());
  filterPanelEl.querySelector('.card-body')
    .insertAdjacentElement('afterbegin', closeBtn);

  // Diet tag click: create removable diet chip
  document.querySelectorAll('.filter-tags span').forEach(tag => {
    tag.addEventListener('click', () => {
      const diet = tag.dataset.text;
      if (selectedDiet.has(diet)) return;
      selectedDiet.add(diet);
      // Update hidden diet
      dietInput.value = diet;

      // Mark radio
      document.querySelectorAll('.filter-tags input[type=radio]').forEach(r => {
        if (r.value === diet) r.checked = true;
      });

      // Create chip
      const chip = document.createElement('div');
      chip.className = 'chip diet-chip';
      chip.textContent = diet + ' ';
      const removeBtn = document.createElement('button');
      removeBtn.className = 'remove-chip';
      removeBtn.title = 'Remove diet';
      removeBtn.innerText = '×';
      chip.appendChild(removeBtn);
      chipArea.appendChild(chip);

      // Remove handler
      removeBtn.addEventListener('click', () => {
        chip.remove();
        selectedDiet.delete(diet);
        dietInput.value = '';
        document.querySelectorAll('.filter-tags input[type=radio]').forEach(r => {
          if (r.value === diet) r.checked = false;
        });
      });
    });
  });

  // Apply Filters button: capture slider/select values into hidden inputs
  applyBtn.addEventListener('click', () => {
    filtersApplied = true;

    // Remove old filter chips
    document.querySelectorAll('.chip.filter-chip').forEach(c => c.remove());

    // Write to hidden
    hiddenMaxCalories.value = calSlider.value;
    hiddenMaxTime.value     = timeSlider.value;
    hiddenDifficulty.value  = diffSelect.value;

    // Create summary chip
    const chip = document.createElement('div');
    chip.className = 'chip filter-chip';
    chip.textContent = `Filters: ≤${hiddenMaxCalories.value} kcal, ≤${hiddenMaxTime.value} min, ${hiddenDifficulty.value || 'Any'}` + ' ';
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-chip';
    removeBtn.title = 'Remove filters';
    removeBtn.innerText = '×';
    chip.appendChild(removeBtn);
    chipArea.appendChild(chip);

    // Remove filters handler
    removeBtn.addEventListener('click', () => {
      chip.remove();
      filtersApplied = false;
      hiddenMaxCalories.value = '';
      hiddenMaxTime.value     = '';
      hiddenDifficulty.value  = '';
      // Reset UI controls to defaults
      calSlider.value = calSlider.defaultValue;
      document.getElementById('calLabel').textContent = calSlider.defaultValue;
      timeSlider.value = timeSlider.defaultValue;
      document.getElementById('timeLabel').textContent = timeSlider.defaultValue;
      diffSelect.value = '';
    });

    // Collapse panel
    bsCollapse.hide();
  });

  // Form submit: if filtersApplied false, clear hidden so backend ignores them
  form.addEventListener('submit', () => {
    if (!filtersApplied) {
      hiddenMaxCalories.value = '';
      hiddenMaxTime.value     = '';
      hiddenDifficulty.value  = '';
    }
    // dietInput already set via diet tag clicks
  });
});