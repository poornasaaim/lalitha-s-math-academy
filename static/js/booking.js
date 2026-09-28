/* ============================================================
   booking.js — Custom dynamic booking form & GSheets slots logic
   ============================================================ */

let selectedBasis = 'hourly';
let selectedDays = [];
let selectedSlot = null;
let selectedMode = 'offline';
let scheduleOption = 'days'; // 'days' or 'daily'
let allSlots = [];

const ALL_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

// ── Open Modal ──────────────────────────────────────────────────
function openBookingModal(basis) {
  selectedBasis = basis;
  selectedDays = [];
  selectedSlot = null;
  selectedMode = 'offline';
  scheduleOption = 'days';

  const overlay = document.getElementById('booking-overlay');
  if (!overlay) return;

  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  // Get DOM elements
  const titleEl = document.getElementById('booking-modal-title');
  const subEl   = document.getElementById('booking-modal-sub');

  const scheduleTypeGrp = document.getElementById('schedule-type-group');
  const monthsGrp       = document.getElementById('months-group');
  const weeksGrp        = document.getElementById('weeks-group');
  const hoursGrp        = document.getElementById('hours-group');
  const numDaysGrp      = document.getElementById('num-days-group');
  const dayPickerGrp    = document.getElementById('day-picker-group');

  // Inputs
  const hoursInput   = document.getElementById('hours-input');
  const numDaysInput = document.getElementById('num-days-input');
  const monthsInput  = document.getElementById('months-input');
  const weeksInput   = document.getElementById('weeks-input');

  // Default input values
  if (hoursInput) hoursInput.value = '1';
  if (numDaysInput) numDaysInput.value = '3';
  if (monthsInput) monthsInput.value = '1';
  if (weeksInput) weeksInput.value = '4';

  // Reset Schedule Option tabs to 'days'
  setScheduleOption('days');

  // Titles & setup based on basis
  if (basis === 'hourly') {
    titleEl.textContent = '⏱️ Book Hourly Session';
    subEl.textContent   = 'Enter the hours needed, choose your available time slot & preferred date.';

    scheduleTypeGrp.classList.add('hidden');
    monthsGrp.classList.add('hidden');
    weeksGrp.classList.add('hidden');
    hoursGrp.classList.remove('hidden');
    numDaysGrp.classList.add('hidden');
    dayPickerGrp.classList.add('hidden');

  } else if (basis === 'weekly') {
    titleEl.textContent = '📆 Book Weekly Plan';
    subEl.textContent   = 'Enter days per week, select your days, hours & recurring time slot.';

    scheduleTypeGrp.classList.add('hidden');
    monthsGrp.classList.add('hidden');
    weeksGrp.classList.remove('hidden');
    hoursGrp.classList.remove('hidden');
    numDaysGrp.classList.remove('hidden');
    dayPickerGrp.classList.remove('hidden');

  } else if (basis === 'monthly') {
    titleEl.textContent = '🗓️ Book Monthly Plan';
    subEl.textContent   = 'Select schedule option (Daily or Specific Days), months, hours & time slot.';

    scheduleTypeGrp.classList.remove('hidden');
    monthsGrp.classList.remove('hidden');
    weeksGrp.classList.add('hidden');
    hoursGrp.classList.remove('hidden');

    document.getElementById('months-label').textContent = '🗓️ Number of Months';

  } else if (basis === 'yearly') {
    titleEl.textContent = '🎓 Book Yearly Plan';
    subEl.textContent   = 'Select months in program, schedule option (Daily or Specific Days), hours & time slot.';

    scheduleTypeGrp.classList.remove('hidden');
    monthsGrp.classList.remove('hidden');
    weeksGrp.classList.add('hidden');
    hoursGrp.classList.remove('hidden');

    document.getElementById('months-label').textContent = '🎓 Duration in Months (e.g., 3, 6, 9, 12 months)';
    if (monthsInput) monthsInput.value = '12';
  }

  // Update layout & render day picker
  updatePlanLayout();

  // Load available slots from GSheets
  loadSlots();
}

// ── Schedule Option (Daily vs Specific Days) ───────────────────
function setScheduleOption(opt) {
  scheduleOption = opt;

  const tabDays  = document.getElementById('tab-schedule-days');
  const tabDaily = document.getElementById('tab-schedule-daily');

  if (tabDays)  tabDays.classList.toggle('active', opt === 'days');
  if (tabDaily) tabDaily.classList.toggle('active', opt === 'daily');

  updatePlanLayout();
}

// ── Update layout based on current plan & schedule option ─────
function updatePlanLayout() {
  const numDaysGrp   = document.getElementById('num-days-group');
  const dayPickerGrp = document.getElementById('day-picker-group');
  const numDaysInput = document.getElementById('num-days-input');

  if (selectedBasis === 'monthly' || selectedBasis === 'yearly') {
    if (scheduleOption === 'daily') {
      // Daily mode
      numDaysGrp.classList.add('hidden');
      dayPickerGrp.classList.remove('hidden');
      selectedDays = [...ALL_DAYS]; // All 7 days including Sunday!
      renderDayPickerStaticAll();
    } else {
      // Specific days mode
      numDaysGrp.classList.remove('hidden');
      dayPickerGrp.classList.remove('hidden');
      const maxD = parseInt(numDaysInput ? numDaysInput.value : '3', 10) || 3;
      renderDayPicker(maxD);
    }
  } else if (selectedBasis === 'weekly') {
    const maxD = parseInt(numDaysInput ? numDaysInput.value : '3', 10) || 3;
    renderDayPicker(maxD);
  } else if (selectedBasis === 'hourly') {
    numDaysGrp.classList.add('hidden');
    dayPickerGrp.classList.add('hidden');
    selectedDays = [];
  }

  updateSlotDisplay();
}

// ── Render Day Picker ──────────────────────────────────────────
function renderDayPicker(maxDays) {
  const container = document.getElementById('day-picker');
  const label = document.getElementById('day-picker-label');
  if (!container) return;

  if (label) {
    label.textContent = selectedBasis === 'hourly'
      ? '📅 Select Preferred Day'
      : `📅 Select ${maxDays} Day(s) of Week`;
  }

  container.innerHTML = '';
  // Ensure selectedDays doesn't exceed maxDays
  if (selectedDays.length > maxDays) {
    selectedDays = selectedDays.slice(0, maxDays);
  }

  ALL_DAYS.forEach(day => {
    const chip = document.createElement('div');
    chip.className = 'day-chip' + (selectedDays.includes(day) ? ' selected' : '');
    chip.textContent = day.slice(0, 3); // Mon, Tue, ..., Sun
    chip.dataset.day = day;
    chip.addEventListener('click', () => toggleDay(chip, day, maxDays));
    container.appendChild(chip);
  });
}

function renderDayPickerStaticAll() {
  const container = document.getElementById('day-picker');
  const label = document.getElementById('day-picker-label');
  if (!container) return;

  if (label) label.textContent = '⚡ Daily Schedule Selected (Monday – Sunday)';

  container.innerHTML = '';
  ALL_DAYS.forEach(day => {
    const chip = document.createElement('div');
    chip.className = 'day-chip selected';
    chip.style.background = 'var(--primary)';
    chip.style.color = '#fff';
    chip.style.cursor = 'default';
    chip.textContent = day.slice(0, 3);
    container.appendChild(chip);
  });
}

function toggleDay(chip, day, maxDays) {
  if (selectedDays.includes(day)) {
    selectedDays = selectedDays.filter(d => d !== day);
    chip.classList.remove('selected');
  } else {
    if (selectedDays.length >= maxDays) {
      const oldest = selectedDays.shift();
      const oldestChip = document.querySelector(`.day-chip[data-day="${oldest}"]`);
      if (oldestChip) oldestChip.classList.remove('selected');
    }
    selectedDays.push(day);
    chip.classList.add('selected');
  }
  updateSlotDisplay();
}

// ── Load & Display Slots from GSheets ─────────────────────────
async function loadSlots() {
  const container = document.getElementById('slots-grid');
  if (container) container.innerHTML = '<p style="color:var(--text-faint);font-size:0.85rem;grid-column:1/-1">Loading available slots from Google Sheets...</p>';

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

  // Filter slots from GSheets based on selected days (or show all unique)
  let relevantSlots = [];

  if (selectedDays.length > 0) {
    const filtered = allSlots.filter(s => selectedDays.includes(s.day));
    // Unique time slots
    const timeSlotCounts = {};
    filtered.forEach(s => {
      if (!timeSlotCounts[s.time_slot]) timeSlotCounts[s.time_slot] = 0;
      if (String(s.is_available).toUpperCase() === 'TRUE') timeSlotCounts[s.time_slot]++;
    });

    const uniqueTimes = [...new Set(allSlots.map(s => s.time_slot))];
    relevantSlots = uniqueTimes.map(ts => ({
      time_slot: ts,
      is_available: timeSlotCounts[ts] !== undefined ? (timeSlotCounts[ts] > 0) : true,
    }));
  } else {
    const seen = {};
    allSlots.forEach(s => {
      if (!seen[s.time_slot]) {
        seen[s.time_slot] = true;
        relevantSlots.push({
          time_slot: s.time_slot,
          is_available: String(s.is_available).toUpperCase() === 'TRUE'
        });
      }
    });
  }

  if (relevantSlots.length === 0) {
    // Default fallback time slots if sheet has no custom slots
    relevantSlots = [
      { time_slot: '4:00 PM - 5:00 PM', is_available: true },
      { time_slot: '5:00 PM - 6:00 PM', is_available: true },
      { time_slot: '6:00 PM - 7:00 PM', is_available: true },
      { time_slot: '7:00 PM - 8:00 PM', is_available: true },
    ];
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

// ── Close Modal ────────────────────────────────────────────────
function closeBookingModal() {
  const overlay = document.getElementById('booking-overlay');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
}

// ── Mode Tabs (Offline / Online) ───────────────────────────────
function setMode(mode) {
  selectedMode = mode;
  document.querySelectorAll('#mode-group .mode-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.mode === mode);
  });
  const meetNote = document.getElementById('meet-note');
  if (meetNote) meetNote.classList.toggle('hidden', mode !== 'online');
}

// ── Submit Booking ─────────────────────────────────────────────
async function submitBooking() {
  const dateInput    = document.getElementById('preferred-date');
  const hoursInput   = document.getElementById('hours-input');
  const numDaysInput = document.getElementById('num-days-input');
  const monthsInput  = document.getElementById('months-input');
  const weeksInput   = document.getElementById('weeks-input');
  const submitBtn    = document.getElementById('booking-submit-btn');

  // Validations
  if (selectedBasis !== 'hourly' && selectedDays.length === 0) {
    showFlash('Please select at least one day.', 'warning');
    return;
  }
  if (!selectedSlot) {
    showFlash('Please select an available time slot.', 'warning');
    return;
  }

  const hoursNeeded = hoursInput ? hoursInput.value : '1';
  const hoursLabel  = hoursNeeded === '1' ? '1 Hour' : `${hoursNeeded} Hours`;

  let quantity = '';
  let daysOfWeekText = selectedDays.join(', ');

  if (selectedBasis === 'hourly') {
    quantity = hoursLabel;
    if (dateInput && dateInput.value) {
      const parts = dateInput.value.split('-');
      if (parts.length === 3) {
        const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        daysOfWeekText = dayNames[d.getDay()] || 'Single Session';
      } else {
        daysOfWeekText = 'Single Session';
      }
    } else {
      daysOfWeekText = 'Single Session';
    }
  } else if (selectedBasis === 'weekly') {
    const w = weeksInput ? weeksInput.value : '4';
    quantity = `${w} Week(s) (${selectedDays.length} days/wk, ${hoursLabel}/session)`;
  } else if (selectedBasis === 'monthly') {
    const m = monthsInput ? monthsInput.value : '1';
    if (scheduleOption === 'daily') {
      daysOfWeekText = 'Daily (Monday – Sunday)';
      quantity = `${m} Month(s) (Daily, ${hoursLabel}/session)`;
    } else {
      quantity = `${m} Month(s) (${selectedDays.length} days/wk, ${hoursLabel}/session)`;
    }
  } else if (selectedBasis === 'yearly') {
    const m = monthsInput ? monthsInput.value : '12';
    if (scheduleOption === 'daily') {
      daysOfWeekText = 'Daily (Monday – Sunday)';
      quantity = `${m} Month(s) / Yearly Program (Daily, ${hoursLabel}/session)`;
    } else {
      quantity = `${m} Month(s) / Yearly Program (${selectedDays.length} days/wk, ${hoursLabel}/session)`;
    }
  }

  const payload = {
    basis:          selectedBasis,
    mode:           selectedMode,
    quantity:       quantity,
    days_of_week:   daysOfWeekText,
    time_slot:      selectedSlot,
    preferred_date: dateInput ? dateInput.value : '',
  };

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Submitting Booking...';
  }

  try {
    const res = await fetch('/api/book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.success) {
      window.location.href = '/confirmation';
    } else {
      showFlash(data.error || 'Failed to process booking. Try again.', 'error');
    }
  } catch (err) {
    showFlash('Network error. Please try again.', 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '📩 Submit Booking';
    }
  }
}

// ── DOM Listeners Setup ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('booking-overlay');
  if (overlay) {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeBookingModal();
    });
  }

  // Hours change listener
  const hoursInput = document.getElementById('hours-input');
  if (hoursInput) {
    hoursInput.addEventListener('change', () => updateSlotDisplay());
  }

  // Number of days change listener
  const numDaysInput = document.getElementById('num-days-input');
  if (numDaysInput) {
    numDaysInput.addEventListener('input', () => updatePlanLayout());
  }

  // Schedule option tabs (Daily vs Specific Days)
  const tabDays  = document.getElementById('tab-schedule-days');
  const tabDaily = document.getElementById('tab-schedule-daily');
  if (tabDays)  tabDays.addEventListener('click', () => setScheduleOption('days'));
  if (tabDaily) tabDaily.addEventListener('click', () => setScheduleOption('daily'));

  // Mode tabs (Offline / Online)
  document.querySelectorAll('#mode-group .mode-tab').forEach(tab => {
    tab.addEventListener('click', () => setMode(tab.dataset.mode));
  });

  // Submit button
  const submitBtn = document.getElementById('booking-submit-btn');
  if (submitBtn) submitBtn.addEventListener('click', submitBooking);
});

// Expose globals for inline HTML handlers
window.openBookingModal = openBookingModal;
window.closeBookingModal = closeBookingModal;
window.setMode = setMode;
window.setScheduleOption = setScheduleOption;

function showFlash(msg, type) {
  if (window.AppUtils && window.AppUtils.showFlash) {
    window.AppUtils.showFlash(msg, type);
  } else {
    alert(msg);
  }
}
