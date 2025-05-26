document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('ingredientsModal');
    const titleEl = document.getElementById('ingredientsModalLabel');
    const countEl = document.getElementById('ingredients-count');
    const listEl  = document.getElementById('ingredients-list');
    const genBtn  = document.getElementById('generate-shopping-list-btn');
    let currentIngredients = [];
  
    function updateCount() {
      const total = currentIngredients.length;
      const have   = listEl.querySelectorAll('input:checked').length;
      countEl.textContent = `${have} of ${total} ingredients available`;
    }
  
    document.querySelectorAll('.view-ingredients-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const title = btn.dataset.title;
        currentIngredients = JSON.parse(btn.dataset.ingredients);
        titleEl.textContent = `Ingredients for ${title}`;
        listEl.innerHTML = '';
        currentIngredients.forEach((ing, i) => {
          const li = document.createElement('li');
          li.className = 'list-group-item d-flex align-items-center bg-white text-dark';
          li.innerHTML = `
            <input type="checkbox" id="ing-${i}" class="form-check-input me-2">
            <label for="ing-${i}" class="flex-grow-1">${ing}</label>
          `;
          li.querySelector('input').addEventListener('change', e => {
            li.querySelector('label')
              .classList.toggle('text-decoration-line-through', e.target.checked);
            updateCount();
          });
          listEl.appendChild(li);
        });
        updateCount();
      });
    });
  
    genBtn.addEventListener('click', async () => {
      const toBuy = Array.from(listEl.querySelectorAll('input'))
        .map((cb, i) => ({ cb, ing: currentIngredients[i] }))
        .filter(x => !x.cb.checked)
        .map(x => x.ing);
  
      if (!toBuy.length) {
        alert('You already have all ingredients! 🎉');
        return;
      }
      const name = prompt('Name your shopping list:');
      if (!name) return;
  
      try {
        const resp = await fetch('/api/shopping-lists', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, items: toBuy })
        });
        if (!resp.ok) throw new Error(await resp.text());
        bootstrap.Modal.getInstance(modalEl).hide();
        alert('Shopping list created!');
        // TODO: Refresh dropdown under profile
      } catch {
        alert('Could not create shopping list.');
      }
    });
  });
  