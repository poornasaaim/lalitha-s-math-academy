/* ============================================================
   main.js — Carousel, Dark/Light Toggle, Animations, Navbar
   ============================================================ */

// ── Theme Toggle ──────────────────────────────────────────────
const THEME_KEY = 'lalitha-theme';

function getTheme() {
  // Default to dark theme — user can switch to light via toggle
  return localStorage.getItem(THEME_KEY) || 'dark';
}

// Apply theme IMMEDIATELY to prevent flash of wrong theme
(function() {
  const saved = localStorage.getItem(THEME_KEY) || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
})();

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  const current = getTheme();
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// ── Navbar Scroll ─────────────────────────────────────────────
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

// ── Mobile Nav ────────────────────────────────────────────────
function initMobileNav() {
  const btn = document.getElementById('mobile-nav-btn');
  const links = document.querySelector('.nav-links');
  if (!btn || !links) return;
  btn.addEventListener('click', () => {
    links.classList.toggle('mobile-open');
    btn.textContent = links.classList.contains('mobile-open') ? '✕' : '☰';
  });
}

// ── Hero Carousel ─────────────────────────────────────────────
function initCarousel(containerId = 'hero-carousel') {
  const track = document.querySelector(`#${containerId} .carousel-track`);
  const slides = document.querySelectorAll(`#${containerId} .carousel-slide`);
  const dots   = document.querySelectorAll(`#${containerId} .carousel-dot`);
  const prevBtn = document.getElementById('carousel-prev');
  const nextBtn = document.getElementById('carousel-next');
  if (!track || slides.length === 0) return;

  let current = 0;
  let autoplay;

  function goTo(index) {
    slides[current].classList.remove('active');
    if (dots[current]) dots[current].classList.remove('active');
    current = (index + slides.length) % slides.length;
    slides[current].classList.add('active');
    if (dots[current]) dots[current].classList.add('active');
    track.style.transform = `translateX(-${current * 100}%)`;
  }

  function startAutoplay() {
    stopAutoplay();
    autoplay = setInterval(() => goTo(current + 1), 5000);
  }

  function stopAutoplay() {
    if (autoplay) clearInterval(autoplay);
  }

  // Init
  slides[0].classList.add('active');
  if (dots[0]) dots[0].classList.add('active');

  // Controls
  if (prevBtn) prevBtn.addEventListener('click', () => { goTo(current - 1); startAutoplay(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { goTo(current + 1); startAutoplay(); });

  dots.forEach((dot, i) => dot.addEventListener('click', () => { goTo(i); startAutoplay(); }));

  // Touch swipe
  let startX = 0;
  track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; stopAutoplay(); }, { passive: true });
  track.addEventListener('touchend', e => {
    const diff = startX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) goTo(current + (diff > 0 ? 1 : -1));
    startAutoplay();
  });

  startAutoplay();
  return { goTo, startAutoplay, stopAutoplay };
}

// ── Scroll Animations ─────────────────────────────────────────
function initScrollAnimations() {
  const elements = document.querySelectorAll('.fade-up');
  if (!elements.length) return;

  const observer = new IntersectionObserver(
    entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    }),
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );
  elements.forEach(el => observer.observe(el));
}

// ── Counter Animation ─────────────────────────────────────────
function animateCounter(el, target, duration = 1500) {
  const start = performance.now();
  const update = now => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target) + (el.dataset.suffix || '');
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

function initCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.dataset.counter);
        animateCounter(entry.target, target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(el => observer.observe(el));
}

// ── Flash Messages ────────────────────────────────────────────
function initFlashMessages() {
  const messages = document.querySelectorAll('.flash-msg');
  messages.forEach(msg => {
    setTimeout(() => msg.remove(), 5000);
    msg.addEventListener('click', () => msg.remove());
  });
}

// ── Pricing Card Hover Glow ───────────────────────────────────
function initPricingCards() {
  const cards = document.querySelectorAll('.pricing-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty('--mouse-x', `${x}%`);
      card.style.setProperty('--mouse-y', `${y}%`);
    });
  });
}

// ── Smooth Scroll ─────────────────────────────────────────────
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// ── Init All ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Apply saved theme
  applyTheme(getTheme());

  // Theme toggle button
  const themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  initNavbarScroll();
  initMobileNav();
  initCarousel('hero-carousel');
  initScrollAnimations();
  initCounters();
  initFlashMessages();
  initPricingCards();
  initSmoothScroll();

  // Dashboard secondary carousel (sideways, same component)
  if (document.getElementById('dash-carousel')) {
    initCarousel('dash-carousel');
  }
});

// Export for use in other scripts
window.AppUtils = { whatsappLink, showFlash };

function whatsappLink(phone, message) {
  return `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
}

function showFlash(message, type = 'info') {
  const container = document.querySelector('.flash-container') || (() => {
    const c = document.createElement('div');
    c.className = 'flash-container';
    document.body.appendChild(c);
    return c;
  })();

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const div = document.createElement('div');
  div.className = `flash-msg flash-${type}`;
  div.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(div);
  setTimeout(() => div.remove(), 5000);
}
