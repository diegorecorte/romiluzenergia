(() => {
  const root = document.querySelector('#equipment-catalog');
  if (!root || root.dataset.staticPreview !== 'true') return;
  const cards = [...root.querySelectorAll('.equipment-card')];
  const brandLinks = [...root.querySelectorAll('[data-catalog-brand]')];
  const kindLinks = [...root.querySelectorAll('[data-catalog-kind]')];
  const mark = (links, key, value) => {
    for (const link of links) {
      if (link.dataset[key] === value) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
  };
  const filter = () => {
    const params = new URLSearchParams(location.search);
    const brand = params.get('marca') || '';
    const kind = params.get('tipo') || '';
    let count = 0;
    for (const card of cards) {
      card.hidden = Boolean((brand && brand !== card.dataset.brand) || (kind && kind !== card.dataset.kind));
      if (!card.hidden) count++;
    }
    mark(brandLinks, 'catalogBrand', brand);
    mark(kindLinks, 'catalogKind', kind);
    root.querySelector('#catalog-products-title').textContent = brand ? `Equipos de ${brand}` : 'Todos los equipos';
    root.querySelector('[role="status"]').textContent = `${count} equipo${count === 1 ? '' : 's'}`;
    root.querySelector('.catalog-empty').hidden = count > 0;
    for (const link of kindLinks) {
      const url = new URL(location.pathname, location.origin);
      if (brand) url.searchParams.set('marca', brand);
      if (link.dataset.catalogKind) url.searchParams.set('tipo', link.dataset.catalogKind);
      link.href = url.pathname + url.search + '#catalog-products';
    }
  };
  root.addEventListener('click', event => {
    const link = event.target.closest('a[data-catalog-brand], a[data-catalog-kind]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    history.pushState(null, '', link.href);
    filter();
    const products = root.querySelector('#catalog-products');
    products.focus({preventScroll: true});
    products.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start'});
  });
  addEventListener('popstate', filter);
  filter();
})();
