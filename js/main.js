const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const navLinks = document.getElementById('navLinks');
const menuBtn = document.getElementById('menuBtn');
if (menuBtn && navLinks) {
  menuBtn.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', String(open));
  });
  navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    menuBtn.setAttribute('aria-expanded', 'false');
  }));
}

const cursor = document.getElementById('cursor');
const cursorRing = document.getElementById('cursorRing');
let mouseX = 0, mouseY = 0, ringX = 0, ringY = 0;
if (!reduceMotion && matchMedia('(pointer:fine)').matches && cursor && cursorRing) {
  window.addEventListener('mousemove', e => {
    mouseX = e.clientX; mouseY = e.clientY;
    cursor.style.opacity = '1'; cursorRing.style.opacity = '1';
    cursor.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
  });
  const follow = () => {
    ringX += (mouseX - ringX) * 0.16;
    ringY += (mouseY - ringY) * 0.16;
    cursorRing.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;
    requestAnimationFrame(follow);
  };
  follow();
  document.querySelectorAll('a,button,[data-tilt]').forEach(el => {
    el.addEventListener('mouseenter', () => document.body.classList.add('link-hover'));
    el.addEventListener('mouseleave', () => document.body.classList.remove('link-hover'));
  });
}

const reveals = document.querySelectorAll('.reveal');
if (reveals.length > 0 && 'IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });
  reveals.forEach(el => revealObserver.observe(el));
} else {
  reveals.forEach(el => el.classList.add('visible'));
}

/* Dynamic Staggered Scroll-triggered Entrance for Landing Choice Cards */
const choiceCards = document.querySelectorAll('.landing-choice-card');
if (choiceCards.length > 0 && 'IntersectionObserver' in window) {
  const choiceObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        choiceObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.16, rootMargin: '0px 0px -40px 0px' });
  choiceCards.forEach(card => choiceObserver.observe(card));
} else {
  choiceCards.forEach(card => card.classList.add('revealed'));
}

const scrollProgress = document.getElementById('scrollProgress');
const timelinePercent = document.getElementById('timelinePercent');
const sections = [...document.querySelectorAll('main section[id]')];
const navItems = [...document.querySelectorAll('.nav-links a')];
function onScroll() {
  const max = document.documentElement.scrollHeight - innerHeight;
  const progress = max > 0 ? scrollY / max : 0;
  if (scrollProgress) {
    scrollProgress.style.width = `${progress * 100}%`;
  }
  if (timelinePercent) {
    timelinePercent.textContent = `${String(Math.round(progress * 100)).padStart(2, '0')}%`;
  }
  let active = sections[0]?.id;
  sections.forEach(section => {
    if (section.getBoundingClientRect().top < innerHeight * 0.42) active = section.id;
  });
  navItems.forEach(item => item.classList.toggle('active', item.getAttribute('href') === `#${active}`));
}
document.addEventListener('scroll', onScroll, { passive: true });
onScroll();

if (!reduceMotion) {
  document.querySelectorAll('[data-tilt]').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5;
      const y = (e.clientY - r.top) / r.height - .5;
      card.style.setProperty('--mouse-x', `${e.clientX - r.left}px`);
      card.style.setProperty('--mouse-y', `${e.clientY - r.top}px`);
      card.style.transform = `translateY(-6px) rotateX(${-y * 6}deg) rotateY(${x * 6}deg)`;
    });
    card.addEventListener('mouseleave', () => card.style.transform = '');
  });
}

function startNetworkCanvas(canvas, options = {}) {
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  let w = 0, h = 0, points = [];
  const count = options.count || 70;
  function resize() {
    const rect = canvas.getBoundingClientRect();
    w = canvas.width = Math.max(1, Math.floor(rect.width * devicePixelRatio));
    h = canvas.height = Math.max(1, Math.floor(rect.height * devicePixelRatio));
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    points = Array.from({ length: count }, () => ({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height,
      vx: (Math.random() - .5) * .42,
      vy: (Math.random() - .5) * .42
    }));
  }
  function frame() {
    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    points.forEach((p, i) => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > rect.width) p.vx *= -1;
      if (p.y < 0 || p.y > rect.height) p.vy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 1.4, 0, Math.PI * 2);
      ctx.fillStyle = i % 7 === 0 ? 'rgba(67,213,199,.75)' : 'rgba(242,212,125,.65)';
      ctx.fill();
      for (let j = i + 1; j < points.length; j++) {
        const q = points[j];
        const dx = p.x - q.x, dy = p.y - q.y;
        const d = Math.hypot(dx, dy);
        if (d < 120) {
          ctx.globalAlpha = (1 - d / 120) * .42;
          ctx.strokeStyle = i % 5 === 0 ? 'rgba(67,213,199,.75)' : 'rgba(214,168,63,.6)';
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(q.x, q.y);
          ctx.stroke();
          ctx.globalAlpha = 1;
        }
      }
    });
    requestAnimationFrame(frame);
  }
  resize();
  window.addEventListener('resize', resize);
  frame();
}
if (!reduceMotion) {
  const bg = document.getElementById('bgCanvas');
  if (bg) startNetworkCanvas(bg, { count: 46 });
  const sc = document.getElementById('signalCanvas');
  if (sc) startNetworkCanvas(sc, { count: 58 });
  const tc = document.getElementById('terminalCanvas');
  if (tc) startNetworkCanvas(tc, { count: 32 });
}

/* ===== Photography Filtering & Lightbox ===== */
const photoGallery = document.getElementById('photoGallery');
if (photoGallery) {
  const filterBtns = document.querySelectorAll('.photo-filter-btn');
  const photoCards = Array.from(photoGallery.querySelectorAll('.photo-card'));
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      
      const filter = btn.getAttribute('data-filter');
      photoCards.forEach(card => {
        const cat = card.getAttribute('data-category');
        if (filter === 'all' || cat === filter) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  const lightbox = document.getElementById('photoLightbox');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxTag = document.getElementById('lightboxTag');
  const lightboxTitle = document.getElementById('lightboxTitle');
  const lightboxDesc = document.getElementById('lightboxDesc');
  const lightboxClose = document.getElementById('lightboxClose');
  const lightboxOverlay = document.getElementById('lightboxOverlay');
  const lightboxPrev = document.getElementById('lightboxPrev');
  const lightboxNext = document.getElementById('lightboxNext');

  let currentIdx = 0;
  function getVisibleCards() {
    return photoCards.filter(c => !c.classList.contains('hidden'));
  }

  function openLightbox(index) {
    const visible = getVisibleCards();
    if (index < 0 || index >= visible.length) return;
    currentIdx = index;
    const card = visible[currentIdx];
    const img = card.querySelector('img');
    const badge = card.querySelector('.photo-card-badge');
    const title = card.querySelector('.photo-card-body h3');
    const desc = card.querySelector('.photo-card-body p');

    if (lightboxImg && img) {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || '';
    }
    if (lightboxTag && badge) lightboxTag.textContent = badge.textContent;
    if (lightboxTitle && title) lightboxTitle.textContent = title.textContent;
    if (lightboxDesc && desc) lightboxDesc.textContent = desc.textContent;

    if (lightbox) {
      lightbox.classList.add('active');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeLightbox() {
    if (lightbox) {
      lightbox.classList.remove('active');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
  }

  photoCards.forEach(card => {
    card.addEventListener('click', () => {
      const visible = getVisibleCards();
      const idx = visible.indexOf(card);
      if (idx !== -1) openLightbox(idx);
    });
  });

  if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
  if (lightboxOverlay) lightboxOverlay.addEventListener('click', closeLightbox);

  if (lightboxPrev) {
    lightboxPrev.addEventListener('click', e => {
      e.stopPropagation();
      const visible = getVisibleCards();
      if (visible.length === 0) return;
      currentIdx = (currentIdx - 1 + visible.length) % visible.length;
      openLightbox(currentIdx);
    });
  }

  if (lightboxNext) {
    lightboxNext.addEventListener('click', e => {
      e.stopPropagation();
      const visible = getVisibleCards();
      if (visible.length === 0) return;
      currentIdx = (currentIdx + 1) % visible.length;
      openLightbox(currentIdx);
    });
  }

  document.addEventListener('keydown', e => {
    if (!lightbox || !lightbox.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    else if (e.key === 'ArrowLeft') {
      const visible = getVisibleCards();
      if (visible.length === 0) return;
      currentIdx = (currentIdx - 1 + visible.length) % visible.length;
      openLightbox(currentIdx);
    } else if (e.key === 'ArrowRight') {
      const visible = getVisibleCards();
      if (visible.length === 0) return;
      currentIdx = (currentIdx + 1) % visible.length;
      openLightbox(currentIdx);
    }
  });
}

// Security Triage Modal Handler
const triageModal = document.getElementById('triageModal');
if (triageModal) {
  const closeBtn = document.getElementById('triageCloseBtn');
  const backdrop = document.getElementById('triageBackdrop');
  const sendWhatsapp = document.getElementById('triageSendWhatsapp');
  const sendEmail = document.getElementById('triageSendEmail');

  const openModal = () => {
    triageModal.classList.add('active');
    triageModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    const msg = document.getElementById('triageMessage');
    if (msg) setTimeout(() => msg.focus(), 150);
  };

  const closeModal = () => {
    triageModal.classList.remove('active');
    triageModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  document.querySelectorAll('.btn-open-triage').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      openModal();
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && triageModal.classList.contains('active')) {
      closeModal();
    }
  });

  
  // Category Chips Selection Handler
  const chips = document.querySelectorAll('.chip-btn');
  const catInput = document.getElementById('triageCategory');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      if (catInput) {
        catInput.value = chip.getAttribute('data-val') || chip.textContent.trim();
      }
    });
  });

  const getTriageData = () => {
    const category = document.getElementById('triageCategory')?.value || 'General Security Consultation';
    const message = document.getElementById('triageMessage')?.value.trim();
    const name = document.getElementById('triageName')?.value.trim() || 'Anonymous';
    const urgency = document.getElementById('triageUrgency')?.value || 'Standard';
    return { category, message, name, urgency };
  };

  if (sendWhatsapp) {
    sendWhatsapp.addEventListener('click', () => {
      const data = getTriageData();
      if (!data.message) {
        const textarea = document.getElementById('triageMessage');
        if (textarea) {
          textarea.focus();
          textarea.style.borderColor = 'var(--gold-2)';
          setTimeout(() => { textarea.style.borderColor = ''; }, 2000);
        }
        return;
      }
      const fullText = `*Security Assessment Request*\n` +
        `• *Name/Handle:* ${data.name}\n` +
        `• *Urgency:* ${data.urgency}\n` +
        `• *Category:* ${data.category}\n\n` +
        `*Case Details / شرح الحالة:*\n${data.message}`;

      const waUrl = `https://wa.me/963960955844?text=${encodeURIComponent(fullText)}`;
      window.open(waUrl, '_blank');
      closeModal();
    });
  }

  if (sendEmail) {
    sendEmail.addEventListener('click', () => {
      const data = getTriageData();
      if (!data.message) {
        const textarea = document.getElementById('triageMessage');
        if (textarea) {
          textarea.focus();
          textarea.style.borderColor = 'var(--gold-2)';
          setTimeout(() => { textarea.style.borderColor = ''; }, 2000);
        }
        return;
      }
      const subject = `Security Assessment: ${data.category}`;
      const body = `Security Assessment Request\n` +
        `Name/Handle: ${data.name}\n` +
        `Urgency: ${data.urgency}\n` +
        `Category: ${data.category}\n\n` +
        `Case Details:\n${data.message}`;

      const mailtoUrl = `mailto:khalilmkhalil0937@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      window.location.href = mailtoUrl;
      closeModal();
    });
  }
}
