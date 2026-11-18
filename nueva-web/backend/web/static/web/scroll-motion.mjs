// Progressive enhancement: the document is readable before this module runs.
export function initScrollStory(root) {
  const doc = root.ownerDocument;
  const win = doc.defaultView;
  const reduced = win.matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches || !win.IntersectionObserver || !win.CSS?.supports('translate', '1px')) return;

  const plan = new Map();
  const stage = (selector, direction = 'up', stagger = 0, columns = 4) => {
    root.querySelectorAll(selector).forEach((node, index) => {
      if (!plan.has(node)) plan.set(node, {
        direction: direction === 'alternate' ? (index % 2 ? 'right' : 'left') : direction,
        delay: (index % columns) * stagger,
      });
    });
  };
  stage('.intro-panel > *', 'up', 55);
  stage('.stats .features > article', 'alternate', 55);
  stage('.section-heading > *', 'up', 55);
  stage('.services > .service', 'alternate', 65, 3);
  stage('.tools-hub > .eyebrow, .tools-hub > h2', 'up', 55);
  stage('.tools-grid > .tool-tile', 'alternate', 55);
  stage('.energy-teaser > img', 'left');
  stage('.energy-teaser > div', 'right', 0);
  stage('.brand-section .eyebrow, .brand-section h2, .brand-section h3, .brand-section .wrap > p');
  stage('.brand-list > li', 'up', 35, 5);
  stage('.finance > img', 'right');
  stage('.finance > div', 'left');
  stage('.benefits .features > article', 'up', 55, 5);
  stage('.reviews > h2, .reviews > p, .reviews > .button, .review-track');
  stage('#preguntas-frecuentes > *', 'up', 45);
  stage(':scope > .section > h2, :scope > .section > p, :scope > .section > .button');
  stage('.project-grid > article', 'alternate', 55, 3);

  // Read layout before writing any classes, and leave the current viewport visible.
  const belowFold = [...plan].filter(([node]) => {
    const box = node.getBoundingClientRect();
    return box.height > 0 && box.top >= win.innerHeight && !node.contains(doc.activeElement);
  });
  const pending = new Set();
  const hero = root.querySelector('.hero');
  const pause = hero?.querySelector('.slide-pause');
  let heroVisible = true;
  let frame = 0;
  let stopped = false;

  function reveal(node, immediate = false) {
    if (!pending.delete(node)) return;
    if (immediate) node.classList.add('scroll-immediate');
    node.classList.remove('scroll-pending');
    observer.unobserve(node);
  }
  const observer = new win.IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.target === hero) {
        heroVisible = entry.isIntersecting;
        if (heroVisible) scheduleHero();
      } else if (entry.isIntersecting) reveal(entry.target);
    }
  }, { threshold: 0, rootMargin: '0px 0px -24px 0px' });

  function updateHero() {
    frame = 0;
    if (stopped || !hero || doc.hidden) return;
    const box = hero.getBoundingClientRect();
    const progress = Math.max(0, Math.min(1, -box.top / Math.max(1, box.height)));
    const paused = pause?.getAttribute('aria-pressed') === 'true';
    const distance = win.innerWidth <= 767 ? 6 : 12;
    hero.style.setProperty('--scroll-hero-shift', `${paused ? 0 : progress * distance}px`);
    hero.style.setProperty('--scroll-copy-shift', `${paused ? 0 : progress * -24}px`);
  }
  function scheduleHero() {
    if (!frame && heroVisible && !doc.hidden && !stopped) frame = win.requestAnimationFrame(updateHero);
  }
  function focusIn(event) {
    const node = event.target.closest?.('.scroll-pending');
    if (node) reveal(node, true);
  }
  function restoreViewport() {
    // Covers history restoration and jumping straight to an anchored section.
    for (const node of pending) {
      const box = node.getBoundingClientRect();
      if (box.top < win.innerHeight && box.bottom > 0) reveal(node, true);
    }
    scheduleHero();
  }
  function stop() {
    if (stopped) return;
    stopped = true;
    if (frame) win.cancelAnimationFrame(frame);
    for (const node of [...pending]) reveal(node, true);
    observer.disconnect();
    root.classList.remove('scroll-motion');
    hero?.style.removeProperty('--scroll-hero-shift');
    hero?.style.removeProperty('--scroll-copy-shift');
    win.removeEventListener('scroll', scheduleHero);
    win.removeEventListener('resize', restoreViewport);
    win.removeEventListener('pageshow', restoreViewport);
    win.removeEventListener('hashchange', restoreViewport);
    doc.removeEventListener('focusin', focusIn);
    doc.removeEventListener('visibilitychange', restoreViewport);
    pause?.removeEventListener('click', scheduleHero);
    reduced.removeEventListener('change', motionPreference);
  }
  function motionPreference(event) { if (event.matches) stop(); }

  try {
    for (const [node, options] of belowFold) {
      node.dataset.scrollDirection = options.direction;
      node.style.setProperty('--scroll-delay', `${options.delay}ms`);
      pending.add(node);
      node.classList.add('scroll-item', 'scroll-pending');
      observer.observe(node);
    }
    root.classList.add('scroll-motion');
    if (hero) observer.observe(hero);
    doc.addEventListener('focusin', focusIn);
    doc.addEventListener('visibilitychange', restoreViewport);
    win.addEventListener('scroll', scheduleHero, { passive: true });
    win.addEventListener('resize', restoreViewport, { passive: true });
    win.addEventListener('pageshow', restoreViewport);
    win.addEventListener('hashchange', restoreViewport);
    pause?.addEventListener('click', scheduleHero);
    reduced.addEventListener('change', motionPreference);
    scheduleHero();
  } catch {
    // Unsupported behaviour must never make the content inaccessible.
    stop();
  }
  return stop;
}

if (typeof document !== 'undefined') {
  const home = document.querySelector('[data-scroll-story]');
  if (home) initScrollStory(home);
}
