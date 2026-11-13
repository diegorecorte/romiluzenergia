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
const groups = [
  ['Nueva instalación solar', 'Instalación aislada', 'Batería', 'Backup (autoconsumo)', 'Ampliación o avería', 'Eólica'],
  ['Trabajo eléctrico', 'Avería', 'Punto de recarga', 'Domótica/seguridad', 'Otro'],
  ['Camper/autocaravana', 'Embarcación', 'Instalación nueva', 'Ampliación', 'Avería'],
  ['Revisar mi factura', 'Buscar tarifa mejor', 'Cambio de comercializadora'],
  ['Placas solares', 'Baterías', 'Punto de recarga', 'Otro trabajo'],
  []
];
const service = document.querySelector('#service');
const need = document.querySelector('#need');
function updateService() {
  const choices = groups[service.selectedIndex - 1] || [];
  need.replaceChildren(new Option('Selecciona una opción', ''));
  choices.forEach(choice => need.add(new Option(choice, choice)));
  need.disabled = !choices.length;
  need.required = !!choices.length;
  document.querySelector('#need-label').hidden = !choices.length;
}
service.addEventListener('change', updateService);
const zone = document.querySelector('#zone');
const town = document.querySelector('#town');
function updateZone() {
  const other = zone.value === 'Otra zona';
  document.querySelector('#town-label').hidden = !other;
  town.required = other;
  town.disabled = !other;
  if (!other) town.value = '';
}
zone.addEventListener('change', updateZone);
const serviceMap = [0, 0, 1, 1, 2];
document.querySelectorAll('[data-service], [data-group]').forEach(a => a.addEventListener('click', () => {
  const group = a.dataset.group === undefined ? serviceMap[Number(a.dataset.service)] : Number(a.dataset.group);
  service.selectedIndex = group + 1;
  updateService();
}));
const form = document.querySelector('#contact-form');
const phone = form.elements.telefono;
phone.addEventListener('input', () => phone.setCustomValidity(''));
form.addEventListener('submit', event => {
  event.preventDefault();
  const digits = phone.value.replace(/[\s().+-]/g, '');
  phone.setCustomValidity(/^\d{9,15}$/.test(digits) ? '' : 'Introduce un teléfono válido de entre 9 y 15 cifras.');
  if (!form.reportValidity()) return;
  const f = new FormData(form);
  if (!String(f.get('nombre')).trim()) {
    form.elements.nombre.setCustomValidity('Escribe tu nombre.');
    form.reportValidity();
    return;
  }
  const text = `Hola, soy ${String(f.get('nombre')).trim()}.\nTeléfono: ${f.get('telefono')}\nServicio: ${f.get('servicio')}\n¿Qué necesito?: ${f.get('necesidad') || 'Contactar con ROMILUZ'}\nZona: ${f.get('zona')}${f.get('municipio') ? ' · ' + f.get('municipio') : ''}\n${f.get('comentario') || ''}`;
  document.querySelector('#form-status').textContent = 'Se abrirá WhatsApp con tu consulta preparada. Pulsa Enviar allí para remitirla.';
  window.open('https://wa.me/34617919944?text=' + encodeURIComponent(text), '_blank', 'noopener,noreferrer');
});
form.elements.nombre.addEventListener('input', () => form.elements.nombre.setCustomValidity(''));
updateService();
updateZone();
