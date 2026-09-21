/* ============================================================
   admin.js — Admin dashboard logic
   ============================================================ */

// ── Sidebar Toggle ─────────────────────────────────────────────
function initSidebar() {
  const sidebar  = document.getElementById('admin-sidebar');
  const main     = document.getElementById('admin-main');
  const toggleBtn = document.getElementById('sidebar-toggle');
  if (!sidebar || !toggleBtn) return;

  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    main.classList.toggle('expanded');
    toggleBtn.textContent = sidebar.classList.contains('collapsed') ? '☰' : '✕';
  });
}

// ── Nav Tabs (sidebar sections) ────────────────────────────────
function initNavTabs() {
  const navItems = document.querySelectorAll('.sidebar-nav-item[data-section]');
  const sections = document.querySelectorAll('.admin-section');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navItems.forEach(n => n.classList.remove('active'));
      sections.forEach(s => s.classList.remove('active'));

      item.classList.add('active');
      const target = document.getElementById(`section-${item.dataset.section}`);
      if (target) target.classList.add('active');
    });
  });
}

// ── Confirm Booking ────────────────────────────────────────────
async function confirmBooking(bookingId) {
  const meetInput = document.getElementById(`meet-${bookingId}`);
  const meetLink  = meetInput ? meetInput.value.trim() : '';
  const btn = document.getElementById(`confirm-btn-${bookingId}`);

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';
  }

  try {
    const res = await fetch('/api/admin/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: bookingId, meet_link: meetLink }),
    });
    const data = await res.json();

    if (data.success) {
      showAdminFlash('Booking confirmed! ✅', 'success');
      // Open WhatsApp to notify student
      if (data.wa_link && !data.auto_sent) {
        setTimeout(() => window.open(data.wa_link, '_blank'), 500);
      }
      // Remove row from pending table
      const row = document.getElementById(`booking-row-${bookingId}`);
      if (row) {
        row.style.opacity = '0.5';
        row.style.pointerEvents = 'none';
        setTimeout(() => {
          row.innerHTML = `<td colspan="10" style="text-align:center;color:var(--success);padding:16px">✅ Confirmed & Notified</td>`;
        }, 600);
      }
    } else {
      showAdminFlash(data.error || 'Failed to confirm booking.', 'error');
    }
  } catch (err) {
    showAdminFlash('Network error. Try again.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '✅ Confirm'; }
  }
}

// ── Send Reminder ──────────────────────────────────────────────
async function sendReminder(bookingId) {
  const btn = document.getElementById(`remind-btn-${bookingId}`);
  if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }

  try {
    const res = await fetch('/api/admin/remind', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: bookingId }),
    });
    const data = await res.json();

    if (data.success) {
      if (data.wa_link && !data.auto_sent) {
        window.open(data.wa_link, '_blank');
        showAdminFlash('WhatsApp opened to send reminder.', 'info');
      } else if (data.auto_sent) {
        showAdminFlash('Reminder sent automatically! ✅', 'success');
      }
    } else {
      showAdminFlash('Could not send reminder.', 'error');
    }
  } catch {
    showAdminFlash('Network error.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '📲 Remind'; }
  }
}

// ── Slots Manager ──────────────────────────────────────────────
function initSlotsManager() {
  const saveBtn = document.getElementById('save-slots-btn');
  if (!saveBtn) return;

  saveBtn.addEventListener('click', async () => {
    const toggles = document.querySelectorAll('.slot-toggle-input');
    const slots = Array.from(toggles).map(t => ({
      day: t.dataset.day,
      time_slot: t.dataset.slot,
      is_available: t.checked ? 'TRUE' : 'FALSE',
    }));

    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner"></span> Saving...';

    try {
      const res = await fetch('/api/admin/slots', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slots }),
      });
      const data = await res.json();
      showAdminFlash(data.success ? 'Slots saved! ✅' : 'Error saving slots.', data.success ? 'success' : 'error');
    } catch {
      showAdminFlash('Network error.', 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = '💾 Save Availability';
    }
  });
}

// ── Carousel Manager ───────────────────────────────────────────
function initCarouselManager() {
  const saveBtn = document.getElementById('save-carousel-btn');
  if (!saveBtn) return;

  saveBtn.addEventListener('click', async () => {
    const rows = document.querySelectorAll('.carousel-row');
    const images = Array.from(rows).map((row, i) => ({
      url:     row.querySelector('.carousel-url-input')?.value.trim() || '',
      caption: row.querySelector('.carousel-caption-input')?.value.trim() || '',
      order:   i + 1,
    })).filter(img => img.url);

    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner"></span> Saving...';

    try {
      const res = await fetch('/api/admin/carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ images }),
      });
      const data = await res.json();
      showAdminFlash(data.success ? 'Carousel updated! ✅' : 'Error updating carousel.', data.success ? 'success' : 'error');
    } catch {
      showAdminFlash('Network error.', 'error');
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = '💾 Save Carousel';
    }
  });
}

// ── Meet Link for Confirmed Bookings ───────────────────────────
async function setMeetLink(bookingId) {
  const input = document.getElementById(`meet-confirmed-${bookingId}`);
  const btn   = document.getElementById(`meet-btn-${bookingId}`);
  if (!input) return;
  const link = input.value.trim();
  if (!link) { showAdminFlash('Please enter a Meet link.', 'warning'); return; }

  if (btn) { btn.disabled = true; btn.textContent = 'Saving...'; }

  try {
    const res = await fetch('/api/admin/meet-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ booking_id: bookingId, meet_link: link }),
    });
    const data = await res.json();
    if (data.success) {
      showAdminFlash('Meet link saved and sent! ✅', 'success');
    } else {
      showAdminFlash('Failed to save meet link.', 'error');
    }
  } catch {
    showAdminFlash('Network error.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '🔗 Send Link'; }
  }
}

// ── Flash Messages ─────────────────────────────────────────────
function showAdminFlash(message, type = 'info') {
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  let container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
  }
  const div = document.createElement('div');
  div.className = `flash-msg flash-${type}`;
  div.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(div);
  setTimeout(() => div.remove(), 5000);
}

// ── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initNavTabs();
  initSlotsManager();
  initCarouselManager();
});

// Expose functions
window.confirmBooking = confirmBooking;
window.sendReminder   = sendReminder;
window.setMeetLink    = setMeetLink;
