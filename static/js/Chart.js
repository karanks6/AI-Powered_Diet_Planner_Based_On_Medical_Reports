document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById('nutritionChart')?.getContext('2d');
  if (!ctx || !window.nutritionData) return;

  const nutrition = window.nutritionData;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Calories', 'Protein', 'Carbs', 'Fat'],
      datasets: [{
        label: 'Daily Nutrition Breakdown',
        data: [
          nutrition.calories || 0,
          nutrition.protein || 0,
          nutrition.carbs || 0,
          nutrition.fat || 0
        ],
        backgroundColor: [
          'rgba(99, 102, 241, 0.7)',
          'rgba(34, 197, 94, 0.7)',
          'rgba(234, 179, 8, 0.7)',
          'rgba(239, 68, 68, 0.7)'
        ],
        borderRadius: 10
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: { y: { beginAtZero: true } }
    }
  });
});


