// main.js - global JS helpers used across pages

document.addEventListener('DOMContentLoaded', () => {
  // Add click handler for any 'Get Started' anchor with id getStartedBtn
  const getStartedBtn = document.getElementById('getStartedBtn');
  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', (e) => {
      // If upload form exists and no file selected, show friendly modal/alert
      const reportFile = document.getElementById('reportFile');
      const hasFile = reportFile && reportFile.files && reportFile.files.length > 0;
      if (!hasFile) {
        e.preventDefault();
        // nicer toast-like message instead of alert
        showWarning('Please upload your medical report (PDF/image) before proceeding.');
      }
    });
  }

  // Basic toast function
  function showWarning(msg) {
    // simple fallback alert for now
    if (!("createElement" in document)) {
      alert(msg);
      return;
    }
    const t = document.createElement('div');
    t.textContent = msg;
    t.style.position = 'fixed';
    t.style.right = '20px';
    t.style.top = '20px';
    t.style.background = 'linear-gradient(90deg,#f59e0b,#fb923c)';
    t.style.color = '#062024';
    t.style.padding = '12px 18px';
    t.style.borderRadius = '10px';
    t.style.boxShadow = '0 8px 24px rgba(15,23,42,0.12)';
    t.style.zIndex = 9999;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  }

  // Demo: attach nicer behavior for demo button if present
  const demoBtn = document.getElementById('demoBtn');
  if (demoBtn) {
    demoBtn.addEventListener('click', () => {
      // You can implement auto-upload demo behaviour here or redirect.
      window.location.href = '/analyze_report';
    });
  }
});
