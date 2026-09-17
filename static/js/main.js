/**
 * LifeLens AI – Main JavaScript
 * Handles UI interactions: mobile sidebar, notifications, charts defaults.
 */

// ── Chart.js global defaults ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (typeof Chart !== 'undefined') {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    Chart.defaults.color = isDark ? '#94A3B8' : '#64748B';
    Chart.defaults.borderColor = isDark ? '#334155' : '#E2E8F0';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.padding = 10;
  }

  // Mobile sidebar toggle
  const sidebar   = document.getElementById('sidebar');
  const sidebarTgl= document.getElementById('sidebarToggle');
  if (sidebarTgl && sidebar && window.innerWidth <= 768) {
    sidebarTgl.addEventListener('click', () => sidebar.classList.toggle('mobile-open'));
    // Close on nav-link click
    sidebar.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => sidebar.classList.remove('mobile-open'));
    });
  }

  // Auto-dismiss flash alerts after 5s
  setTimeout(() => {
    document.querySelectorAll('.flash-container .alert').forEach(el => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 300);
    });
  }, 5000);

  // Notifications panel loader
  const panel = document.getElementById('notifBody');
  if (panel) {
    document.querySelector('[data-bs-target="#notificationsPanel"]')
      ?.addEventListener('click', loadNotifications);
  }

  // Activate Bootstrap tooltips
  document.querySelectorAll('[title]').forEach(el => new bootstrap.Tooltip(el, { trigger: 'hover' }));
});

// ── Notifications ─────────────────────────────────────────────────────────
async function loadNotifications() {
  const panel = document.getElementById('notifBody');
  if (!panel) return;
  panel.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div></div>';
  // Fetch unread recommendations
  try {
    const res = await fetch('/chatbot/weekly-summary');
    const data = await res.json();
    if (data.summary) {
      panel.innerHTML = `<div class="p-2 small" style="white-space:pre-line">${markdownToHtmlSimple(data.summary)}</div>`;
    }
  } catch (e) {
    panel.innerHTML = '<p class="text-muted small p-3">Could not load notifications.</p>';
  }
}

function markdownToHtmlSimple(text) {
  return text
    .replace(/## (.*)/g, '<h6 class="fw-bold mt-2">$1</h6>')
    .replace(/### (.*)/g, '<div class="fw-semibold">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.*)/gm, '<li style="margin-left:12px">$1</li>')
    .replace(/\n/g, '<br>');
}

// ── Number formatting helpers ─────────────────────────────────────────────
function formatRupee(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

// ── Progress bar animation ─────────────────────────────────────────────────
function animateProgressBars() {
  document.querySelectorAll('.progress-bar').forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      bar.style.transition = 'width .8s ease-in-out';
      bar.style.width = target;
    });
  });
}
document.addEventListener('DOMContentLoaded', animateProgressBars);
