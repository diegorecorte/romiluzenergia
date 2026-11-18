'use strict';
const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
menu.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});
nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  nav.classList.remove('open');
  menu.setAttribute('aria-expanded', 'false');
  nav.querySelectorAll('details').forEach(d => { d.open = false; });
}));
// Carrusel independiente, con controles, pausa y respeto por movimiento reducido.
const hero = document.querySelector('.hero');
if (hero) {
  const slides = [...hero.querySelectorAll('.slide')];
  const dots = [...hero.querySelectorAll('.slide-dots button')];
  const pause = hero.querySelector('.slide-pause');
  let index = 0;
  let paused = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let autoplayTimer;
  const autoplayDelay = 20000;
  function show(next) {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== index; });
    dots.forEach((dot, i) => dot.setAttribute('aria-pressed', String(i === index)));
  }
  function updatePause() {
    pause.textContent = paused ? 'Reanudar' : 'Pausar';
    pause.setAttribute('aria-pressed', String(paused));
  }
  function restartAutoplay() {
    clearInterval(autoplayTimer);
    if (paused || document.hidden || slides.length < 2) return;
    autoplayTimer = setInterval(() => {
      // Mantener visible un enlace mientras se utiliza con el teclado.
      if (!slides[index].contains(document.activeElement)) show(index + 1);
    }, autoplayDelay);
  }
  function navigate(next) { show(next); restartAutoplay(); }
  hero.querySelector('.slide-prev').addEventListener('click', () => navigate(index - 1));
  hero.querySelector('.slide-next').addEventListener('click', () => navigate(index + 1));
  dots.forEach((dot, i) => dot.addEventListener('click', () => navigate(i)));
  pause.addEventListener('click', () => { paused = !paused; updatePause(); restartAutoplay(); });
  hero.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); navigate(index - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); navigate(index + 1); }
  });
  document.addEventListener('visibilitychange', restartAutoplay);
  updatePause();
  restartAutoplay();
}
const leadForm = document.querySelector('#lead-form');
if (leadForm) {
  const groups = JSON.parse(document.querySelector('#service-groups').textContent);
  const service = leadForm.elements.servicio;
  const need = leadForm.elements.necesidad;
  const zone = leadForm.elements.zona;
  const town = leadForm.elements.municipio;
  function syncService() {
    const previous = need.value;
    const choices = groups[service.value] || [];
    need.replaceChildren(new Option('Selecciona una opción', ''));
    choices.forEach(value => need.add(new Option(value, value)));
    if (choices.includes(previous)) need.value = previous;
    need.disabled = !choices.length;
    need.required = !!choices.length;
    leadForm.querySelector('[data-field="necesidad"]').hidden = !choices.length;
  }
  function syncZone() {
    const visible = zone.value === 'Otra zona';
    town.disabled = !visible;
    town.required = visible;
    leadForm.querySelector('[data-field="municipio"]').hidden = !visible;
  }
  service.addEventListener('change', syncService);
  zone.addEventListener('change', syncZone);
  syncService();syncZone();
  const attachment = leadForm.elements.factura;
  if (attachment) {
    attachment.addEventListener('change', () => {
      const file = attachment.files[0];
      const status = document.querySelector('#attachment-status');
      attachment.setCustomValidity('');
      if (!file) { status.textContent = ''; return; }
      let error = '';
      if (file.size > 8 * 1024 * 1024) error = 'El archivo no puede superar 8 MB.';
      else if (!/\.(pdf|jpe?g|png)$/i.test(file.name)) error = 'Selecciona una factura PDF o una imagen JPG/PNG.';
      attachment.setCustomValidity(error);
      status.textContent = error || 'Archivo seleccionado: ' + file.name + '. Aún no se ha enviado.';
      if (error) attachment.reportValidity();
    });
  }
  const phone = leadForm.elements.telefono;
  function validate() {
    const digits = phone.value.replace(/[\s().+-]/g, '');
    phone.setCustomValidity(/^\d{9,15}$/.test(digits) ? '' : 'Introduce un teléfono válido de entre 9 y 15 cifras.');
  }
  phone.addEventListener('input', () => phone.setCustomValidity(''));
  leadForm.addEventListener('submit', event => { validate();if (!leadForm.reportValidity()) event.preventDefault(); });
  document.querySelector('#whatsapp').addEventListener('click', () => {
    validate();
    const privacy = leadForm.elements.privacidad;
    const required = privacy.required;
    privacy.required = false;
    const valid = leadForm.reportValidity();
    privacy.required = required;
    if (!valid) return;
    const d = new FormData(leadForm);
    const message = `Hola, soy ${d.get('nombre')}.\nTeléfono: ${d.get('telefono')}\nServicio: ${d.get('servicio')}\n¿Qué necesito?: ${d.get('necesidad') || 'Contactar con ROMILUZ'}\nZona: ${d.get('zona')}${d.get('municipio') ? ' · '+d.get('municipio') : ''}\n${d.get('comentario') || ''}`;
    const file = leadForm.elements.factura;
    document.querySelector('#form-status').textContent = file && file.files.length ? 'El archivo no se adjunta a WhatsApp. Usa Enviar solicitud para la carga privada.' : 'Pulsa Enviar en WhatsApp para remitir tu consulta.';
    window.open('https://wa.me/34617919944?text='+encodeURIComponent(message), '_blank', 'noopener,noreferrer');
  });
}
if (document.querySelector('#energy-experience')) {
  import('./energy-realistic.mjs?v=meter-1').catch(() => {
    const notice = document.querySelector('#energy-loading');
    if (notice) notice.textContent = 'No se ha podido cargar la vista 3D. Recarga la página o consulta la explicación del funcionamiento que aparece debajo.';
  });
}
