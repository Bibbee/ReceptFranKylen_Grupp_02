// static/js/settings.js

document.addEventListener('DOMContentLoaded', () => {
  const trigger = document.getElementById('settingsTrigger');
  const panel   = document.getElementById('settings-panel');
  const toggle  = document.getElementById('darkModeToggle');

  // 1) Show/hide the settings panel
  trigger.addEventListener('click', e => {
    panel.classList.toggle('d-none');
    // Prevent the click from bubbling up and immediately closing the panel
    e.stopPropagation();
  });

  // 2) Initialize toggle button from previous preference
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    toggle.checked = true;
  }

  // 3) Listen for toggle changes
  toggle.addEventListener('change', () => {
    if (toggle.checked) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'false');
    }
  });

  // 4) Click outside the panel = close the panel
  document.addEventListener('click', e => {
    if (!panel.contains(e.target) && !trigger.contains(e.target)) {
      panel.classList.add('d-none');
    }
  });
});
