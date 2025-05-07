document.addEventListener("DOMContentLoaded", function () {
    const chipContainer = document.getElementById("selected-chip");
    const inputField = document.getElementById("ingredients-input");
  
    document.querySelectorAll('.filter-tags span').forEach(tag => {
      tag.addEventListener('click', () => {
        const value = tag.dataset.text;
  
        // Kolla om redan tillagd
        if (inputField.value.toLowerCase().includes(value.toLowerCase())) return;
  
        // Lägg till i inputfältet
        inputField.value = inputField.value
          ? inputField.value + ', ' + value
          : value;
  
        // Visa chip visuellt
        chipContainer.innerHTML = '';
        const chip = document.createElement("div");
        chip.className = "chip";
        chip.innerHTML = `${value} <button class="remove-chip" title="Remove">×</button>`;
  
        chip.querySelector(".remove-chip").addEventListener("click", () => {
          chip.remove();
          // Ta bort value från inputfältet
          inputField.value = inputField.value
            .split(',')
            .map(v => v.trim())
            .filter(v => v.toLowerCase() !== value.toLowerCase())
            .join(', ');
          // Avmarkera radioknapp
          document.querySelectorAll('.filter-tags input[type="radio"]').forEach(r => r.checked = false);
        });
  
        chipContainer.appendChild(chip);
      });
    });
  });
  