/* =============================================================================
   ROOTSTOCK — site.js
   Progressive interaction layer. Every behaviour is opt-in via data attributes
   so pages stay readable and nothing breaks if JS fails to load.
========================================================================== */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------------------------------------------------------------- theme */
  var THEME_KEY = 'rootstock:theme';
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
    $$('[data-theme-toggle]').forEach(function (b) {
      b.setAttribute('aria-label', t === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
      b.setAttribute('aria-pressed', String(t === 'dark'));
    });
  }
  function initTheme() {
    var saved = null;
    try { saved = localStorage.getItem(THEME_KEY); } catch (e) {}
    var prefers = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    applyTheme(saved || prefers);
    $$('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
      });
    });
  }

  /* --------------------------------------------------------------- header */
  function initHeader() {
    var header = $('[data-header]');
    if (!header) return;
    var last = window.scrollY;
    var onScroll = function () {
      var y = window.scrollY;
      header.classList.toggle('is-stuck', y > 24);
      // hide on scroll down, reveal on scroll up (never over the drawer)
      if (!document.body.classList.contains('is-locked')) {
        header.classList.toggle('is-hidden', y > 420 && y > last + 6);
      }
      last = y;
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* --------------------------------------------------------------- drawer */
  function initDrawer() {
    var burger = $('[data-burger]');
    var drawer = $('[data-drawer]');
    if (!burger || !drawer) return;
    var setOpen = function (open) {
      burger.setAttribute('aria-expanded', String(open));
      drawer.classList.toggle('is-open', open);
      drawer.setAttribute('aria-hidden', String(!open));
      document.body.classList.toggle('is-locked', open);
      if (open) { var f = drawer.querySelector('a, button'); if (f) f.focus({ preventScroll: true }); }
    };
    burger.addEventListener('click', function () {
      setOpen(burger.getAttribute('aria-expanded') !== 'true');
    });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) { setOpen(false); burger.focus(); }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 900 && drawer.classList.contains('is-open')) setOpen(false);
    });
  }

  /* --------------------------------------------- scroll reveal (in + out) */
  function initReveal() {
    var items = $$('[data-reveal], .stagger, .split-text, .underline-sketch');
    if (!items.length) return;
    if (reduced || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var el = entry.target;
        if (entry.isIntersecting) {
          el.classList.add('is-visible');
          el.classList.remove('is-exiting');
          if (el.hasAttribute('data-reveal-once')) io.unobserve(el);
        } else if (el.hasAttribute('data-reveal-exit')) {
          // only soften when the element has scrolled off the TOP of the viewport
          el.classList.toggle('is-exiting', entry.boundingClientRect.top < 0);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* --------------------------------------------------- headline word wipe */
  function initSplitText() {
    $$('[data-split]').forEach(function (el) {
      if (el.dataset.splitDone) return;
      var lines = el.textContent.trim().split('\n');
      el.textContent = '';
      lines.forEach(function (line, li) {
        line.trim().split(/\s+/).forEach(function (word, i) {
          var wrap = document.createElement('span');
          wrap.className = 'split-text';
          var inner = document.createElement('span');
          inner.className = 'word';
          inner.textContent = word;
          inner.style.transitionDelay = (li * 0.06 + i * 0.05) + 's';
          wrap.appendChild(inner);
          el.appendChild(wrap);
          el.appendChild(document.createTextNode(' '));
        });
        if (li < lines.length - 1) el.appendChild(document.createElement('br'));
      });
      el.dataset.splitDone = '1';
      el.classList.add('split-host');
      requestAnimationFrame(function () {
        $$('.split-text', el).forEach(function (s) { s.classList.add('is-visible'); });
      });
    });
  }

  /* ------------------------------------------------------- number counters */
  function initCounters() {
    var els = $$('[data-count]');
    if (!els.length) return;
    var run = function (el) {
      var target = parseFloat(el.dataset.count);
      var dec = parseInt(el.dataset.decimals || '0', 10);
      var dur = parseInt(el.dataset.duration || '1600', 10);
      if (reduced) { el.textContent = target.toLocaleString(undefined, { minimumFractionDigits: dec, maximumFractionDigits: dec }); return; }
      var t0 = performance.now();
      var tick = function (now) {
        var p = Math.min(1, (now - t0) / dur);
        var eased = 1 - Math.pow(1 - p, 4);
        el.textContent = (target * eased).toLocaleString(undefined, { minimumFractionDigits: dec, maximumFractionDigits: dec });
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if (!('IntersectionObserver' in window)) { els.forEach(run); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { run(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.5 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ------------------------------------------------------ progress meters */
  function initMeters() {
    var els = $$('[data-meter]');
    if (!els.length) return;
    var fill = function (el) { el.style.width = Math.max(0, Math.min(100, +el.dataset.meter)) + '%'; };
    if (!('IntersectionObserver' in window)) { els.forEach(fill); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { fill(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.4 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* --------------------------------------------------------------- tabs */
  function initTabs() {
    $$('[data-tabs]').forEach(function (group) {
      var tabs = $$('[role="tab"]', group);
      var select = function (tab) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute('aria-selected', String(on));
          t.tabIndex = on ? 0 : -1;
          var panel = document.getElementById(t.getAttribute('aria-controls'));
          if (panel) panel.hidden = !on;
        });
      };
      tabs.forEach(function (tab, i) {
        tab.addEventListener('click', function () { select(tab); });
        tab.addEventListener('keydown', function (e) {
          var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
          if (!d) return;
          e.preventDefault();
          var next = tabs[(i + d + tabs.length) % tabs.length];
          next.focus(); select(next);
        });
      });
    });
  }

  /* ---------------------------------------------------------- accordions */
  function initAccordion() {
    $$('[data-accordion]').forEach(function (acc) {
      var single = acc.hasAttribute('data-accordion-single');
      $$('.acc-trigger', acc).forEach(function (btn) {
        btn.addEventListener('click', function () {
          var item = btn.closest('.acc-item');
          var open = item.classList.contains('is-open');
          if (single) {
            $$('.acc-item', acc).forEach(function (i) {
              i.classList.remove('is-open');
              var b = $('.acc-trigger', i); if (b) b.setAttribute('aria-expanded', 'false');
            });
          }
          item.classList.toggle('is-open', !open);
          btn.setAttribute('aria-expanded', String(!open));
        });
      });
    });
  }

  /* ------------------------------------------------------------ carousel */
  function initCarousel() {
    $$('[data-carousel]').forEach(function (car) {
      var track = $('[data-carousel-track]', car);
      var prev = $('[data-carousel-prev]', car);
      var next = $('[data-carousel-next]', car);
      if (!track) return;
      var step = function () {
        var first = track.firstElementChild;
        return first ? first.getBoundingClientRect().width + 24 : 320;
      };
      var sync = function () {
        var max = track.scrollWidth - track.clientWidth - 2;
        if (prev) prev.disabled = track.scrollLeft <= 2;
        if (next) next.disabled = track.scrollLeft >= max;
      };
      if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: reduced ? 'auto' : 'smooth' }); });
      if (next) next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: reduced ? 'auto' : 'smooth' }); });
      track.addEventListener('scroll', sync, { passive: true });
      window.addEventListener('resize', sync);
      sync();
    });
  }

  /* -------------------------------------------------------------- filters */
  function initFilters() {
    $$('[data-filter-group]').forEach(function (group) {
      var targetSel = group.dataset.filterGroup;
      var items = $$(targetSel + ' [data-tags]');
      $$('[data-filter]', group).forEach(function (chip) {
        chip.addEventListener('click', function () {
          $$('[data-filter]', group).forEach(function (c) { c.classList.remove('is-active'); c.setAttribute('aria-pressed', 'false'); });
          chip.classList.add('is-active');
          chip.setAttribute('aria-pressed', 'true');
          var f = chip.dataset.filter;
          var shown = 0;
          items.forEach(function (item) {
            var match = f === 'all' || item.dataset.tags.split(' ').indexOf(f) > -1;
            item.style.display = match ? '' : 'none';
            if (match) {
              shown++;
              item.style.animation = 'none';
              void item.offsetWidth;
              if (!reduced) item.style.animation = 'grow-in .5s var(--ease-expo) both';
            }
          });
          var empty = $(group.dataset.filterEmpty || '[data-filter-empty]');
          if (empty) empty.hidden = shown > 0;
          var count = $('[data-filter-count]');
          if (count) count.textContent = shown;
        });
      });
    });
  }

  /* -------------------------------------------------------------- marquee */
  function initMarquee() {
    $$('[data-marquee]').forEach(function (track) {
      if (track.dataset.cloned) return;
      track.innerHTML += track.innerHTML;   // seamless loop
      track.dataset.cloned = '1';
    });
  }

  /* ------------------------------------------------------------- parallax */
  function initParallax() {
    var els = $$('[data-parallax]');
    if (!els.length || reduced) return;
    var ticking = false;
    var update = function () {
      var vh = window.innerHeight;
      els.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var speed = parseFloat(el.dataset.parallax) || 0.12;
        var offset = (r.top + r.height / 2 - vh / 2) * speed;
        el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
      });
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  /* ----------------------------------------------------------- tilt cards */
  function initTilt() {
    if (reduced || window.matchMedia('(hover: none)').matches) return;
    $$('[data-tilt]').forEach(function (el) {
      var max = parseFloat(el.dataset.tilt) || 6;
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'perspective(900px) rotateX(' + (-py * max).toFixed(2) + 'deg) rotateY(' + (px * max).toFixed(2) + 'deg) translateY(-4px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* ------------------------------------------------------ magnetic buttons */
  function initMagnetic() {
    if (reduced || window.matchMedia('(hover: none)').matches) return;
    $$('[data-magnetic]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.22;
        var y = (e.clientY - r.top - r.height / 2) * 0.32;
        el.style.transform = 'translate(' + x.toFixed(1) + 'px,' + (y - 2).toFixed(1) + 'px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* ------------------------------------------------- scroll progress + top */
  function initScrollUi() {
    var bar = $('[data-progress]');
    var top = $('[data-to-top]');
    var onScroll = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? window.scrollY / h : 0;
      if (bar) bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      if (top) top.classList.toggle('is-shown', window.scrollY > 640);
    };
    if (top) top.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    });
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* --------------------------------------------------- scroll-spy (in page) */
  function initSpy() {
    var links = $$('[data-spy] a');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    links.forEach(function (l) {
      var id = l.getAttribute('href').slice(1);
      var sec = document.getElementById(id);
      if (sec) map[id] = l;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (l) { l.classList.remove('is-active'); });
          if (map[e.target.id]) map[e.target.id].classList.add('is-active');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { io.observe(document.getElementById(id)); });
  }

  /* ---------------------------------------------------------------- toasts */
  var toastHost;
  function toast(message, opts) {
    opts = opts || {};
    if (!toastHost) {
      toastHost = document.createElement('div');
      toastHost.className = 'toast-stack';
      toastHost.setAttribute('role', 'status');
      toastHost.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastHost);
    }
    var el = document.createElement('div');
    el.className = 'toast';
    el.innerHTML = '<span class="toast-ico" aria-hidden="true">' +
      '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>' +
      '</span><span></span>';
    el.lastChild.textContent = message;
    toastHost.appendChild(el);
    setTimeout(function () {
      el.classList.add('is-leaving');
      setTimeout(function () { el.remove(); }, 400);
    }, opts.duration || 4200);
  }

  /* ------------------------------------------------------ page transitions */
  function initTransitions() {
    if (reduced) return;
    var veil = $('[data-veil]');
    if (!veil) return;
    document.body.classList.add('is-entering');
    setTimeout(function () { document.body.classList.remove('is-entering'); }, 700);
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      var href = a.getAttribute('href');
      if (!href || a.target === '_blank' || a.hasAttribute('download') || a.dataset.noTransition !== undefined) return;
      if (href.charAt(0) === '#' || href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) return;
      if (a.origin && a.origin !== location.origin) return;
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      if (a.pathname === location.pathname && a.search === location.search) return;
      e.preventDefault();
      veil.classList.add('is-out');
      setTimeout(function () { location.href = a.href; }, 420);
    });
    window.addEventListener('pageshow', function (e) {
      if (e.persisted) veil.classList.remove('is-out');
    });
  }

  /* ------------------------------------------------------------- misc bits */
  function initMisc() {
    $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
    // mark the current page in every nav
    var path = location.pathname.split('/').pop() || 'index.html';
    $$('[data-nav] a').forEach(function (a) {
      var href = (a.getAttribute('href') || '').split('/').pop();
      if (href === path) a.setAttribute('aria-current', 'page');
    });
    // copy-to-clipboard (design system tokens)
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-copy]');
      if (!btn) return;
      var text = btn.dataset.copy;
      var done = function () { toast('Copied ' + text); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else { done(); }
    });
  }

  /* ------------------------------------------------------------------ boot */
  function boot() {
    initTheme(); initHeader(); initDrawer(); initSplitText(); initReveal();
    initCounters(); initMeters(); initTabs(); initAccordion(); initCarousel();
    initFilters(); initMarquee(); initParallax(); initTilt(); initMagnetic();
    initScrollUi(); initSpy(); initTransitions(); initMisc();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  window.Rootstock = { toast: toast, reduced: reduced, $: $, $$: $$ };
})();
