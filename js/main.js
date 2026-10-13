
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const navLinks = document.getElementById('navLinks');
const menuBtn = document.getElementById('menuBtn');
menuBtn.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', String(open));
});
navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  navLinks.classList.remove('open');
  menuBtn.setAttribute('aria-expanded', 'false');
}));

const cursor = document.getElementById('cursor');
const cursorRing = document.getElementById('cursorRing');
let mouseX = 0, mouseY = 0, ringX = 0, ringY = 0;
if (!reduceMotion && matchMedia('(pointer:fine)').matches) {
  window.addEventListener('mousemove', e => {
    mouseX = e.clientX; mouseY = e.clientY;
    cursor.style.opacity = 1; cursorRing.style.opacity = 1;
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
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.14 });
reveals.forEach(el => revealObserver.observe(el));

const scrollProgress = document.getElementById('scrollProgress');
const timelinePercent = document.getElementById('timelinePercent');
const sections = [...document.querySelectorAll('main section[id]')];
const navItems = [...document.querySelectorAll('.nav-links a')];
function onScroll() {
  const max = document.documentElement.scrollHeight - innerHeight;
  const progress = max > 0 ? scrollY / max : 0;
  scrollProgress.style.width = `${progress * 100}%`;
  timelinePercent.textContent = `${String(Math.round(progress * 100)).padStart(2, '0')}%`;
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
      card.style.transform = `translateY(-4px) rotateX(${-y * 5}deg) rotateY(${x * 5}deg)`;
    });
    card.addEventListener('mouseleave', () => card.style.transform = '');
  });
}

function startNetworkCanvas(canvas, options = {}) {
  const ctx = canvas.getContext('2d');
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
  startNetworkCanvas(document.getElementById('bgCanvas'), { count: 46 });
  startNetworkCanvas(document.getElementById('signalCanvas'), { count: 58 });
}

