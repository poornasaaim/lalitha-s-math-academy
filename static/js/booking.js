/* ============================================================
   booking.js — Booking form logic, slot picker, day picker
   ============================================================ */

let selectedBasis = null;
let selectedDays  = [];
let selectedSlot  = null;
let selectedMode  = 'offline';
let allSlots      = [];

// Max days per basis
const MAX_DAYS = {
  hourly:  1,
  weekly:  3,
  monthly: 3,
  yearly:  3,
};

// ── Open booking modal ─────────────────────────────────────────
function openBookingModal(basis) {
  selectedBasis = basis;
  selectedDays  = [];
  selectedSlot  = null;
  selectedMode  = 'offline';

  const overlay = document.getElementById('booking-overlay');
  if (!overlay) return;

  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  // Update modal heading
  const titles = {
    hourly:  '📅 Book Hourly Session',
    weekly:  '📆 Book Weekly Plan',
    monthly: '🗓️ Book Monthly Plan',
    yearly:  '🎓 Book Yearly Plan',
  };
  const subs = {
    hourly:  'Choose your preferred time slot for a 1-hour Mathematics session.',
    weekly:  'Choose 3 days per week and a recurring time slot.',
    monthly: 'Choose 3 days/week for the full month.',
    yearly:  'Long-term yearly plan — choose your recurring schedule.',
  };
  document.getElementById('booking-modal-title').textContent = titles[basis] || 'Book a Session';
  document.getElementById('booking-modal-sub').textContent   = subs[basis] || '';

  // Show/hide quantity field
  const qtyGroup  = document.getElementById('qty-group');
  const qtyLabel  = document.getElementById('qty-label');
  const qtyInput  = document.getElementById('qty-input');

  if (basis === 'hourly') {
    qtyLabel.textContent = 'Number of Hours';
    qtyInput.placeholder = 'e.g. 2';
    qtyGroup.classList.remove('hidden');
  } else if (basis === 'weekly') {
    qtyLabel.textContent = 'Number of Weeks';
    qtyInput.placeholder = 'e.g. 4';
    qtyGroup.classList.remove('hidden');
  } else if (basis === 'monthly') {
    qtyLabel.textContent = 'Number of Months';
    qtyInput.placeholder = 'e.g. 3';
    qtyGroup.classList.remove('hidden');
  } else if (basis === 'yearly') {
    qtyGroup.classList.add('hidden');
  }

  // Render day picker
  renderDayPicker(basis);

  // Load slots
  loadSlots();
}

// ── Close modal ────────────────────────────────────────────────
function closeBookingModal() {
  const overlay = document.getElementById('booking-overlay');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
}

// ── Day Picker ─────────────────────────────────────────────────
const ALL_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

function renderDayPicker(basis) {
  const container = document.getElementById('day-picker');
  if (!container) return;

  const maxDays = MAX_DAYS[basis] || 1;
  container.innerHTML = '';
  container.previousElementSibling.textContent =
    basis === 'hourly' ? 'Preferred Day' : `Choose Days (max ${maxDays})`;

  ALL_DAYS.forEach(day => {
    const chip = document.createElement('div');
    chip.className = 'day-chip';
    chip.textContent = day.slice(0, 3);
    chip.dataset.day = day;
    chip.addEventListener('click', () => toggleDay(chip, day, maxDays));
    container.appendChild(chip);
  });
}

function toggleDay(chip, day, maxDays) {
  if (chip.classList.contains('disabled')) return;

  if (chip.classList.contains('selected')) {
    chip.classList.remove('selected');
    selectedDays = selectedDays.filter(d => d !== day);
  } else {
    if (selectedDays.length >= maxDays) {
      // Deselect the oldest if at max
      const oldest = document.querySelector(`.day-chip[data-day="${selectedDays[0]}"]`);
      if (oldest) oldest.classList.remove('selected');
      selectedDays.shift();
    }
    chip.classList.add('selected');
    selectedDays.push(day);
  }
  updateSlotDisplay();
}

// ── Load & Render Slots ────────────────────────────────────────
async function loadSlots() {
  try {
    const res = await fetch('/api/slots');
    allSlots = await res.json();
  } catch {
    allSlots = [];
  }
  updateSlotDisplay();
}

function updateSlotDisplay() {
  const container = document.getElementById('slots-grid');
  if (!container) return;

  // Get slots relevant to selected days
  let relevantSlots;
  if (selectedDays.length > 0) {
    relevantSlots = allSlots.filter(s => selectedDays.includes(s.day));
    // Unique time slots available on ALL selected days
    const timeSlotCounts = {};
    relevantSlots.forEach(s => {
      if (!timeSlotCounts[s.time_slot]) timeSlotCounts[s.time_slot] = 0;
      if (String(s.is_available).toUpperCase() === 'TRUE') timeSlotCounts[s.time_slot]++;
    });
    // A slot is available if it exists for all selected days
    const uniqueTimes = [...new Set(relevantSlots.map(s => s.time_slot))];
    relevantSlots = uniqueTimes.map(ts => ({
      time_slot: ts,
      is_available: timeSlotCounts[ts] >= selectedDays.length,
    }));
  } else {
    // Show all unique slots
    const seen = {};
    relevantSlots = allSlots.reduce((acc, s) => {
      if (!seen[s.time_slot]) {
        seen[s.time_slot] = true;
        acc.push({ time_slot: s.time_slot, is_available: String(s.is_available).toUpperCase() === 'TRUE' });
      }
      return acc;
    }, []);
  }

  if (relevantSlots.length === 0) {
    container.innerHTML = '<p style="color:var(--text-faint);font-size:0.85rem;grid-column:1/-1">No slots available for selected days.</p>';
    return;
  }

  container.innerHTML = '';
  relevantSlots.forEach(slot => {
    const chip = document.createElement('div');
    chip.className = 'slot-chip' +
      (slot.is_available ? '' : ' unavailable') +
      (selectedSlot === slot.time_slot ? ' selected' : '');
    chip.textContent = slot.time_slot;
    chip.dataset.slot = slot.time_slot;
    if (slot.is_available) {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.slot-chip').forEach(c => c.classList.remove('selected'));
        chip.classList.add('selected');
        selectedSlot = slot.time_slot;
      });
    }
    container.appendChild(chip);
  });
}

// ── Mode Tabs ──────────────────────────────────────────────────
function setMode(mode) {
  selectedMode = mode;
  document.querySelectorAll('.mode-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.mode === mode);
  });
  const meetNote = document.getElementById('meet-note');
  if (meetNote) meetNote.classList.toggle('hidden', mode !== 'online');
}

// ── Submit Booking ─────────────────────────────────────────────
async function submitBooking() {
  const qtyInput = document.getElementById('qty-input');
  const dateInput = document.getElementById('preferred-date');
  const submitBtn = document.getElementById('booking-submit-btn');

  // Validate
  if (selectedDays.length === 0) {
    showFlash('Please select at least one day.', 'warning');
    return;
  }
  if (!selectedSlot) {
    showFlash('Please select a time slot.', 'warning');
    return;
  }

  const qty = qtyInput ? qtyInput.value.trim() : '1';

  const payload = {
    basis:          selectedBasis,
    mode:           selectedMode,
    quantity:       qty || '1',
    days_of_week:   selectedDays.join(', '),
    time_slot:      selectedSlot,
    preferred_date: dateInput ? dateInput.value : '',
  };

  // Loading state
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Saving...';
  }

  try {
    const res = await fetch('/api/book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.success) {
      // Redirect to confirmation page
      window.location.href = '/confirmation';
    } else {
      showFlash(data.error || 'Something went wrong. Please try again.', 'error');
    }
  } catch (err) {
    showFlash('Network error. Please check your connection.', 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '📩 Submit Booking';
    }
  }
}

// ── Close on overlay click ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('booking-overlay');
  if (overlay) {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeBookingModal();
    });
  }

  // Mode tabs
  document.querySelectorAll('.mode-tab').forEach(tab => {
    tab.addEventListener('click', () => setMode(tab.dataset.mode));
  });

  // Submit button
  const submitBtn = document.getElementById('booking-submit-btn');
  if (submitBtn) submitBtn.addEventListener('click', submitBooking);
});

// Expose for inline onclick
window.openBookingModal = openBookingModal;
window.closeBookingModal = closeBookingModal;
window.setMode = setMode;

// Reuse showFlash from main.js
function showFlash(msg, type) {
  if (window.AppUtils && window.AppUtils.showFlash) {
    window.AppUtils.showFlash(msg, type);
  }
}
