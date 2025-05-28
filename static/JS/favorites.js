// Handle clicks on favorite star buttons to save a recipe to the user's favorites and protect the /favorites navigation

document.addEventListener('DOMContentLoaded', async () => {
  // Read login state from body attribute
  const isLoggedIn = document.body.dataset.loggedIn === 'true';

  // -----------------------------------
  // AJAX helper for sending favorite
  // -----------------------------------
  async function sendFavorite(formData) {
    try {
      const res = await fetch('/favorite', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (res.ok) {
        const data = await res.json().catch(() => ({}));
        if (data.ok) {
          new bootstrap.Toast(document.getElementById('toastSaved')).show();
        } else {
          new bootstrap.Toast(document.getElementById('toastExists')).show();
        }
      } else {
        // Unauthorized or server error
        if (res.status === 401 && !isLoggedIn) {
          // Not logged in: defer action
          return;
        }
        alert('Something went wrong: ' + res.status);
      }
    } catch (error) {
      console.error('Error saving favorite:', error);
      alert('A network error occurred.');
    }
  }

  // -----------------------------------
  // Replay pending favorite after login
  // -----------------------------------
  const pendingFav = sessionStorage.getItem('pendingFavorite');
  if (isLoggedIn && pendingFav) {
    sessionStorage.removeItem('pendingFavorite');
    const recipeData = JSON.parse(pendingFav);
    const formData = new FormData();
    Object.entries(recipeData).forEach(([k, v]) => formData.append(k, v));
    await sendFavorite(formData);
    // After replay and successful save, redirect to favorites page
    window.location.href = '/favorites';
  }

  // -----------------------------------
  // Protect header "Favorites" link
  // -----------------------------------
  const headerFavLink = document.getElementById('favoritesLink');
  if (headerFavLink) {
    headerFavLink.addEventListener('click', e => {
      if (!isLoggedIn) {
        e.preventDefault();
        sessionStorage.setItem('pendingNavigateFavorites', '1');
        new bootstrap.Modal(document.getElementById('loginModal')).show();
      }
    });
  }

  // Replay pending navigation after login
  if (isLoggedIn && sessionStorage.getItem('pendingNavigateFavorites')) {
    sessionStorage.removeItem('pendingNavigateFavorites');
    window.location.href = '/favorites';
  }

  // -----------------------------------
  // Favorite-star button handlers
  // -----------------------------------
  document.querySelectorAll('.favorite-star').forEach(button => {
    button.addEventListener('click', async () => {
      // Collect recipe data
      const recipeData = {
        recipe_id:        button.dataset.recipeId,
        title:            button.dataset.title,
        image:            button.dataset.image,
        difficulty:       button.dataset.difficulty || 'Unknown',
        ready_in_minutes: button.dataset.time       || 'Unknown',
        servings:         button.dataset.servings   || 'Unknown',
        nutrition:        button.dataset.nutrition  || 'Information missing',
        instructions:     button.dataset.instructions || 'No instructions available.',
        ingredients:      button.dataset.ingredients
      };

      const formData = new FormData();
      Object.entries(recipeData).forEach(([k, v]) => formData.append(k, v));

      if (!isLoggedIn) {
        // Defer until after login
        sessionStorage.setItem('pendingFavorite', JSON.stringify(recipeData));
        new bootstrap.Modal(document.getElementById('loginModal')).show();
        return;
      }

      // If logged in, send immediately and then redirect
      await sendFavorite(formData);
      window.location.href = '/favorites';
    });
  });
});
