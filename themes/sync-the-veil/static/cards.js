(() => {
  const form = document.querySelector('.card-filters');
  const cards = [...document.querySelectorAll('[data-card]')];
  const count = document.querySelector('#card-count');
  const empty = document.querySelector('.card-empty');
  const search = form.elements.q;
  const keys = ['q', 'faction', 'type', 'set'];
  const normalize = (text) => text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const searchable = new Map(cards.map(card => [card, normalize(card.dataset.search)]));

  function filterCards(updateURL = true) {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const matches = terms.every(term => searchable.get(card).includes(term)) &&
        (!form.elements.faction.value || card.dataset.faction === form.elements.faction.value) &&
        (!form.elements.type.value || card.dataset.type === form.elements.type.value) &&
        (!form.elements.set.value || card.dataset.set === form.elements.set.value);
      card.hidden = !matches;
      if (matches) visible++;
    });
    count.textContent = `${visible} of ${cards.length} cards`;
    empty.hidden = visible !== 0;
    if (updateURL) {
      const url = new URL(location.href);
      keys.forEach(key => {
        const value = form.elements[key].value.trim();
        if (value) url.searchParams.set(key, value);
        else url.searchParams.delete(key);
      });
      const linkedCard = cards.find(card => `#${card.id}` === url.hash);
      if (linkedCard?.hidden) url.hash = '';
      history.replaceState(null, '', url);
    }
  }

  function restoreFilters() {
    const params = new URLSearchParams(location.search);
    keys.forEach(key => { form.elements[key].value = params.get(key) || ''; });
    filterCards(false);
    revealLinkedCard();
  }

  function revealLinkedCard() {
    const target = cards.find(card => `#${card.id}` === location.hash);
    if (target?.hidden) {
      keys.forEach(key => { form.elements[key].value = ''; });
      filterCards();
      target.scrollIntoView();
    }
  }

  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', () => filterCards());
  form.addEventListener('reset', () => {
    // Native reset updates the controls after the reset event is dispatched.
    requestAnimationFrame(() => filterCards());
  });
  document.querySelector('[data-clear-cards]').addEventListener('click', () => {
    form.reset();
    search.focus();
  });
  window.addEventListener('popstate', restoreFilters);
  window.addEventListener('hashchange', revealLinkedCard);
  restoreFilters();
})();
