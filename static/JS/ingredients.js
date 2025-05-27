// static/js/ingredients.js

document.addEventListener('DOMContentLoaded', () => {
  // Element
  const ingredientsModalEl = document.getElementById('ingredientsModal');
  const titleEl            = document.getElementById('ingredientsModalLabel');
  const countEl            = document.getElementById('ingredients-count');
  const listEl             = document.getElementById('ingredients-list');
  const genBtn             = document.getElementById('generate-shopping-list-btn');

  // Name-list modal
  const nameListModalEl    = document.getElementById('nameListModal');
  const listNameInput      = document.getElementById('listNameInput');
  const confirmListNameBtn = document.getElementById('confirmListNameBtn');

  const isLoggedIn         = document.body.dataset.loggedIn === 'true';
  let currentIngredients   = [];
  let pendingItems         = null;

  // Uppdatera counter i modal
  function updateCount() {
    const total = currentIngredients.length;
    const have  = listEl.querySelectorAll('input:checked').length;
    countEl.textContent = `${have} of ${total} ingredients available`;
  }

  // Popupa name-list modal om man är inloggad
  function showNameModal(items) {
    pendingItems = items;
    listNameInput.value = '';
    listNameInput.classList.remove('is-invalid');
    new bootstrap.Modal(nameListModalEl).show();
  }

  // POSTa shoppinglist till API
  async function postShoppingList(name, items) {
    try {
      const resp = await fetch('/api/shopping-lists', {
        method: 'POST',
        headers: { 'Content-Type':'application/json' },
        body: JSON.stringify({ name, items })
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        alert(err.error || 'Could not create shopping list.');
        return false;
      }
      return true;
    } catch (err) {
      console.error(err);
      alert('Network error—please try again later.');
      return false;
    }
  }

  // 1) Klick på ingrediens-knapp -> fyll modal
  document.querySelectorAll('.ingredients-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const title = btn.dataset.title;
      currentIngredients = JSON.parse(btn.dataset.ingredients);

      titleEl.textContent = `Ingredients for ${title}`;
      listEl.innerHTML   = '';

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

  // 2) Klick på "Generate shopping list"
  genBtn.addEventListener('click', () => {
    const toBuy = Array.from(listEl.querySelectorAll('input'))
      .map((cb, i) => ({ cb, ing: currentIngredients[i] }))
      .filter(x => !x.cb.checked)
      .map(x => x.ing);

    if (!toBuy.length) {
      alert('You already have all ingredients! 🎉');
      return;
    }

    if (!isLoggedIn) {
      // Visa login-modal om inte inloggad
      new bootstrap.Modal(document.getElementById('loginModal')).show();
      return;
    }

    // Inloggad → visa name-list modal
    showNameModal(toBuy);
  });

  // 3) After login + redirect (t.ex från index), om pendingItems finns → visa name-list
  const pending = sessionStorage.getItem('pendingShoppingItems');
  if (isLoggedIn && pending) {
    sessionStorage.removeItem('pendingShoppingItems');
    showNameModal(JSON.parse(pending));
  }

  // 4) Bekräfta lista-namn och POST
  confirmListNameBtn.addEventListener('click', async () => {
    const name = listNameInput.value.trim();
    if (!name) {
      listNameInput.classList.add('is-invalid');
      listNameInput.focus();
      return;
    }
    const ok = await postShoppingList(name, pendingItems);
    if (ok) {
      bootstrap.Modal.getInstance(nameListModalEl).hide();
      bootstrap.Modal.getInstance(ingredientsModalEl).hide();
      alert('Shopping list created!');
      // TODO: refresha dropdown under profil
    }
  });
});
