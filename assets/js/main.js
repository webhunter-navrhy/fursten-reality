/* Fürsten Reality — native scroll, IntersectionObserver, no animation loops at rest */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* nav state */
  const nav = $('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', scrollY > 30);
  onScroll(); addEventListener('scroll', onScroll, { passive: true });

  /* mobile menu */
  const burger = $('.burger'), menu = $('.menu');
  if (burger && menu) {
    const set = (open) => {
      menu.classList.toggle('open', open); burger.classList.toggle('open', open);
      document.body.classList.toggle('menu-open', open); burger.setAttribute('aria-expanded', open);
      document.documentElement.style.overflow = open ? 'hidden' : '';
    };
    burger.addEventListener('click', () => set(!menu.classList.contains('open')));
    $$('a', menu).forEach((a) => a.addEventListener('click', () => set(false)));
    addEventListener('keydown', (e) => e.key === 'Escape' && set(false));
  }

  /* reveals */
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }),
    { rootMargin: '0px 0px -7% 0px', threshold: 0.06 });
  $$('.rv').forEach((el) => io.observe(el));

  /* listing filters */
  const grid = $('[data-grid]');
  if (grid) {
    const cards = $$('.lcard', grid), empty = $('.empty-note');
    const apply = (f) => {
      let n = 0;
      cards.forEach((c) => {
        const [k, v] = f.split(':');
        const ok = f === 'all' || (k === 'kind' ? c.dataset.kind === v : c.dataset.type === v);
        c.classList.toggle('hide', !ok); if (ok) { n++; c.classList.add('in'); }
      });
      if (empty) empty.hidden = n > 0;
    };
    $$('.fchip').forEach((b) => b.addEventListener('click', () => {
      $$('.fchip').forEach((x) => x.classList.toggle('on', x === b)); apply(b.dataset.f);
    }));
  }

  /* lightbox (groups by data-lb) with swipe + keys */
  const lb = $('.lb');
  if (lb) {
    const img = $('img', lb), cnt = $('.lb-count', lb), cap = $('.lb-cap', lb);
    let list = [], i = 0, lastFocus = null;
    const show = () => {
      const a = list[i]; img.style.opacity = '0';
      const n = new Image(); n.onload = () => { img.src = n.src; img.style.opacity = '1'; }; n.src = a.getAttribute('href');
      cnt.textContent = `${i + 1} / ${list.length}`; cap.textContent = a.dataset.cap || '';
      const nx = list[(i + 1) % list.length]; if (nx) { const p = new Image(); p.src = nx.getAttribute('href'); }
    };
    const open = (group, k) => {
      list = $$(`[data-lb="${group}"]`); if (!list.length) return;
      i = Math.max(0, k); lastFocus = document.activeElement; show();
      lb.hidden = false; document.body.classList.add('lb-open'); document.documentElement.style.overflow = 'hidden'; $('.lb-x', lb).focus();
    };
    const close = () => { lb.hidden = true; document.body.classList.remove('lb-open'); document.documentElement.style.overflow = ''; img.src = ''; lastFocus && lastFocus.focus(); };
    const go = (d) => { i = (i + d + list.length) % list.length; show(); };
    document.addEventListener('click', (e) => {
      const a = e.target.closest('[data-lb]');
      if (a && !lb.contains(a)) {
        e.preventDefault();
        const g = a.dataset.lb === 'strip' ? 'strip' : a.dataset.lb;
        open(g, $$(`[data-lb="${g}"]`).indexOf(a));
      }
      const o = e.target.closest('[data-open]'); if (o) open(o.dataset.open, 0);
    });
    $('.lb-x', lb).addEventListener('click', close);
    $('.lb-p', lb).addEventListener('click', () => go(-1));
    $('.lb-n', lb).addEventListener('click', () => go(1));
    lb.addEventListener('click', (e) => { if (e.target === lb || e.target.classList.contains('lb-stage')) close(); });
    addEventListener('keydown', (e) => {
      if (lb.hidden) return;
      if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') go(-1); if (e.key === 'ArrowRight') go(1);
    });
    let x0 = null, y0 = 0;
    lb.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    lb.addEventListener('touchend', (e) => {
      if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) go(dx < 0 ? 1 : -1); else if (dy > 90) close();
    }, { passive: true });
  }

  /* mobile photo strip counter */
  const strip = $('[data-strip]');
  if (strip) {
    const out = $('[data-strip-i]');
    let t = 0;
    strip.addEventListener('scroll', () => { cancelAnimationFrame(t); t = requestAnimationFrame(() => { out.textContent = Math.round(strip.scrollLeft / strip.clientWidth) + 1; }); }, { passive: true });
  }

  /* click-to-load map + video (no third-party requests until asked) */
  $$('[data-map]').forEach((m) => $('button', m).addEventListener('click', () => {
    m.innerHTML = `<iframe src="${m.dataset.map}" loading="lazy" title="Mapa – orientačná poloha" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>`;
  }));
  $$('[data-yt]').forEach((b) => b.addEventListener('click', () => {
    b.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.yt}?autoplay=1&rel=0" title="Video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;
  }));

  /* "Požiadať o pôdorys" → prefill message */
  $$('[data-ask]').forEach((a) => a.addEventListener('click', () => {
    const ta = $('#obhliadka textarea'); if (ta && !ta.value.includes(a.dataset.ask)) ta.value = (ta.value.trim() + ' ' + a.dataset.ask).trim();
  }));

  /* forms → WebHunter form API → e-mail; confirmation in place */
  const t0 = Date.now();
  $$('form[data-form]').forEach((f) => {
    const err = $('.form-err', f), done = $('.form-done', f);
    f.addEventListener('input', (e) => { const fl = e.target.closest('.fld, .consent'); if (fl) fl.classList.remove('bad'); });
    f.addEventListener('submit', async (e) => {
      e.preventDefault(); err.textContent = '';
      const fields = {}; let bad = null;
      $$('input, textarea, select', f).forEach((el) => {
        if (!el.name || el.name === 'website' || el.closest('.hp')) return;
        if ((el.type === 'radio' || el.type === 'checkbox') && !el.checked) return;
        const v = el.value.trim(); if (!v) return;
        fields[el.name] = fields[el.name] ? fields[el.name] + ', ' + v : v;
      });
      const req = (sel, cond, msg) => { const el = $(sel, f); if (el && !cond(el)) { (el.closest('.fld') || el.closest('.consent')).classList.add('bad'); bad = bad || [el, msg]; } };
      req('[name="Meno"]', (el) => el.value.trim().length > 1, 'Vyplňte prosím meno.');
      $$('.fld input[required]:not([name="Meno"]), .fld textarea[required]', f).forEach((el) => { if (!el.value.trim()) { el.closest('.fld').classList.add('bad'); bad = bad || [el, 'Vyplňte prosím označené polia.']; } });
      const tel = $('[name="Telefón"]', f), mail = $('[name="E-mail"]', f);
      if (tel && mail && !tel.value.trim() && !mail.value.trim()) { tel.closest('.fld').classList.add('bad'); mail.closest('.fld').classList.add('bad'); bad = bad || [tel, 'Nechajte mi prosím telefón alebo e-mail, aby som Vám mohla odpovedať.']; }
      if (mail && mail.value.trim() && !/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(mail.value.trim())) { mail.closest('.fld').classList.add('bad'); bad = bad || [mail, 'E-mailová adresa nevyzerá správne.']; }
      req('[name="Súhlas"]', (el) => el.checked, 'Pre odoslanie prosím potvrďte súhlas so spracovaním údajov.');
      if (bad) { err.textContent = bad[1]; bad[0].focus({ preventScroll: false }); return; }
      const payload = { type: f.dataset.form, fields, page: location.href.split('#')[0], hp: ($('[name="website"]', f) || {}).value || '', ms: Date.now() - t0 };
      if (f.dataset.listingTitle) payload.listing = { id: f.dataset.listingId, title: f.dataset.listingTitle, url: f.dataset.listingUrl };
      f.classList.add('busy'); const b = $('button[type=submit] span', f); const bt = b.textContent; b.textContent = 'Odosielam…';
      try {
        const r = await fetch(f.dataset.api, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok || !j.ok) throw new Error(j.error || 'Správu sa nepodarilo odoslať.');
        f.classList.add('sent'); done.focus({ preventScroll: true });
        const top = f.getBoundingClientRect().top; if (top < 80) scrollBy({ top: top - 110, behavior: reduce ? 'auto' : 'smooth' });
      } catch (x) {
        err.innerHTML = `${x.message} Skúste to prosím znova alebo zavolajte na <a class="u" href="${($('.mbar-call') || { getAttribute: () => '#' }).getAttribute('href')}">telefón</a>.`;
      } finally { f.classList.remove('busy'); b.textContent = bt; }
    });
  });
})();
