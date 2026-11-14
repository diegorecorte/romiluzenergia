(() => {
  const root = document.querySelector('#equipment-catalog');
  if (!root || root.dataset.staticPreview !== 'true') return;
  const form = root.querySelector('form');
  const brand = form.elements.marca;
  const kind = form.elements.tipo;
  const cards = [...root.querySelectorAll('.equipment-card')];
  const params = new URLSearchParams(location.search);
  const setOption = (select, value) => {
    select.value = [...select.options].some(option => option.value === value) ? value : '';
  };
  const filter = () => {
    let count = 0;
    for (const card of cards) {
      card.hidden = Boolean((brand.value && brand.value !== card.dataset.brand) || (kind.value && kind.value !== card.dataset.kind));
      if (!card.hidden) count++;
    }
    root.querySelector('[role="status"]').textContent = `${count} equipo${count === 1 ? '' : 's'}`;
    root.querySelector('.catalog-empty').hidden = count > 0;
  };
  setOption(brand, params.get('marca') || '');
  setOption(kind, params.get('tipo') || '');
  filter();
  form.addEventListener('submit', event => {
    event.preventDefault();
    const next = new URLSearchParams();
    if (brand.value) next.set('marca', brand.value);
    if (kind.value) next.set('tipo', kind.value);
    history.replaceState(null, '', location.pathname + (next.size ? '?' + next : ''));
    filter();
  });
})();
