document.addEventListener('DOMContentLoaded', () => {
  const trigger = document.getElementById('settingsTrigger');
  const panel   = document.getElementById('settings-panel');
  const toggle  = document.getElementById('darkModeToggle');

  trigger.addEventListener('click', e => {
    panel.classList.toggle('d-none');
    e.stopPropagation();
  });

  // ← Init on load: both set the switch *and* apply the class
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    toggle.checked = true;
  }

  toggle.addEventListener('change', () => {
    if (toggle.checked) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'false');
    }
  });

  document.addEventListener('click', e => {
    if (!panel.contains(e.target) && !trigger.contains(e.target)) {
      panel.classList.add('d-none');
    }
  });
});
