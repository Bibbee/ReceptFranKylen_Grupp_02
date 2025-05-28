/**
 * @fileoverview Implements weekly meal planning functionality, storing plans in localStorage
 * and handling UI interactions for adding, removing, and clearing meals for the current week.
 */

document.addEventListener('DOMContentLoaded', () => {
    /**
     * Indicates whether the user is logged in, based on a data-attribute set on <body>.
     * @type {boolean}
     */
    const isLoggedIn = document.body.dataset.loggedIn === 'true';
    
    /**
     * Holds the title of the currently selected recipe for planning.
     * @type {string}
     */
    let selectedRecipe = '';
  
    /**
     * List of day names for display in the planner (Monday – Sunday).
     * @type {string[]}
     */
    const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
    /**
     * Container element for rendering each day's meal boxes.
     * @type {HTMLElement}
     */
    const weekContainer = document.getElementById('weekPlanContainer');
  
    /**
     * Computes ISO date strings for Monday through Sunday of the current week.
     * @returns {string[]} Array of dates in YYYY-MM-DD format.
     */
    function getCurrentWeekDates() {
      const today = new Date();
      // getDay(): Sunday=0, Monday=1, ..., Saturday=6
      const dayOfWeek = today.getDay();
      const monday = new Date(today);
      // Calculate offset to Monday: (dayOfWeek + 6) % 7 shifts Sunday->6, Monday->0, etc.
      monday.setDate(today.getDate() - ((dayOfWeek + 6) % 7));
      
      // Build array of 7 dates starting from Monday
      return Array.from({ length: 7 }, (_, i) => {
        const date = new Date(monday);
        date.setDate(monday.getDate() + i);
        return date.toISOString().split('T')[0];
      });
    }
  
    /**
     * Renders the weekly view based on stored meal plans in localStorage.
     * Clears container and creates a column for each day, listing meals or a placeholder.
     */
    function refreshWeekView() {
      // Retrieve stored plans or initialize empty object
      const plans = JSON.parse(localStorage.getItem('mealPlans') || '{}');
      weekContainer.innerHTML = '';
  
      const weekDates = getCurrentWeekDates();
      weekDates.forEach((dateStr, index) => {
        const meals = plans[dateStr] || [];
  
        // Create Bootstrap column for this day
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';
  
        // Create card-like box for the day's meals
        const box = document.createElement('div');
        box.className = 'day-box p-3 rounded shadow-sm bg-white text-dark';
  
        // Header with day name and date
        let content = `<h5>${daysOfWeek[index]} <small class=\"text-muted\">(${dateStr})</small></h5>`;
  
        if (meals.length > 0) {
          content += '<ul class=\"mt-2\">';
          meals.forEach((meal, i) => {
            content += `
              <li class=\"d-flex justify-content-between align-items-center\">
                ${meal}
                <span class=\"ms-2 text-danger fs-3\" role=\"button\" style=\"cursor: pointer;\" onclick=\"removeMeal('${dateStr}', ${i})\">×</span>
              </li>`;
          });
          content += '</ul>';
        } else {
          // Display placeholder when no meals planned
          content += '<em>Nothing planned</em>';
        }
  
        box.innerHTML = content;
        col.appendChild(box);
        weekContainer.appendChild(col);
      });
    }
  
    /**
     * Removes a meal entry from the specified date and re-renders the view.
     * @param {string} dateStr - The date key in YYYY-MM-DD format.
     * @param {number} index - Index of the meal to remove in the array.
     */
    window.removeMeal = function (dateStr, index) {
      const plans = JSON.parse(localStorage.getItem('mealPlans') || '{}');
      if (plans[dateStr]) {
        plans[dateStr].splice(index, 1);
        if (plans[dateStr].length === 0) {
          delete plans[dateStr];
        }
        localStorage.setItem('mealPlans', JSON.stringify(plans));
        refreshWeekView();
      }
    };
  
    /**
     * Clears all stored meal plans after user confirmation, then refreshes the view.
     */
    window.clearWeekPlan = function () {
      if (confirm('Are you sure you want to clear the entire weekly plan?')) {
        localStorage.removeItem('mealPlans');
        refreshWeekView();
      }
    };
  
    /**
     * Limits the date picker input to the current week (Monday–Sunday) and defaults value to today.
     */
    function limitDatePickerToCurrentWeek() {
      const dateInput = document.getElementById('mealDate');
      const today = new Date();
      const dayOfWeek = today.getDay();
  
      const monday = new Date(today);
      monday.setDate(today.getDate() - ((dayOfWeek + 6) % 7));
  
      const sunday = new Date(monday);
      sunday.setDate(monday.getDate() + 6);
  
      const formatDate = d => d.toISOString().split('T')[0];
      dateInput.min = formatDate(monday);
      dateInput.max = formatDate(sunday);
      dateInput.value = formatDate(today);
    }
  
    /**
     * Checks if a given date string falls within the current week range.
     * @param {string} dateStr - Date in YYYY-MM-DD format.
     * @returns {boolean} True if within Monday–Sunday of this week.
     */
    function isDateInCurrentWeek(dateStr) {
      const inputDate = new Date(dateStr);
      const today = new Date();
      const dayOfWeek = today.getDay();
  
      const monday = new Date(today);
      monday.setDate(today.getDate() - ((dayOfWeek + 6) % 7));
      monday.setHours(0, 0, 0, 0);
  
      const sunday = new Date(monday);
      sunday.setDate(monday.getDate() + 6);
      sunday.setHours(23, 59, 59, 999);
  
      return inputDate >= monday && inputDate <= sunday;
    }
  
    // Attach click handlers to all "Plan Meal" buttons
    document.querySelectorAll('.meal-plan-btn').forEach(button => {
      button.addEventListener('click', event => {
        event.preventDefault();
        selectedRecipe = button.getAttribute('data-title');
  
        if (!isLoggedIn) {
          // Store pending recipe and prompt login if user is not authenticated
          sessionStorage.setItem('pendingMealRecipe', selectedRecipe);
          new bootstrap.Modal(document.getElementById('loginModal')).show();
          return;
        }
  
        // Populate modal with selected recipe title and show planning UI
        document.getElementById('planMealTitle').textContent = selectedRecipe;
        limitDatePickerToCurrentWeek();
        new bootstrap.Modal(document.getElementById('planMealModal')).show();
      });
    });
  
    /**
     * Saves the selected recipe to localStorage if the date is valid, then updates the view.
     */
    const saveBtn = document.getElementById('saveMealPlanBtn');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => {
        const date = document.getElementById('mealDate').value;
        if (!date || !selectedRecipe) return;
  
        if (!isDateInCurrentWeek(date)) {
          alert('You can only plan meals for this week.');
          return;
        }
  
        const plans = JSON.parse(localStorage.getItem('mealPlans') || '{}');
        if (!plans[date]) plans[date] = [];
        plans[date].push(selectedRecipe);
        localStorage.setItem('mealPlans', JSON.stringify(plans));
  
        // Hide modal and refresh display
        bootstrap.Modal.getInstance(document.getElementById('planMealModal')).hide();
        refreshWeekView();
      });
    }
  
    // If user just logged in after clicking "Plan Meal", resume planning flow
    const pendingRecipe = sessionStorage.getItem('pendingMealRecipe');
    if (isLoggedIn && pendingRecipe) {
      sessionStorage.removeItem('pendingMealRecipe');
      selectedRecipe = pendingRecipe;
  
      document.getElementById('planMealTitle').textContent = selectedRecipe;
      limitDatePickerToCurrentWeek();
      new bootstrap.Modal(document.getElementById('planMealModal')).show();
    }
  
    // Initial render of the week view on page load
    refreshWeekView();
  });
  