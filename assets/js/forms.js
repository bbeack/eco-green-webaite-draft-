/* =============================================================================
   ROOTSTOCK — forms.js
   The information-capture layer: validation, submission handling and local
   persistence for every form on the site.

   A static site has no server, so submissions are validated client-side and
   written to localStorage under `rootstock:leads`. Point `Rootstock.Forms.
   endpoint` at a real collector (Formspree, a Lambda, your CRM) and every form
   will POST there instead — the markup and UX do not change.
========================================================================== */
(function () {
  'use strict';

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var STORE = 'rootstock:leads';
  var CONFIG = { endpoint: null, storeLocally: true };

  /* ------------------------------------------------------------ storage */
  function readAll() {
    try { return JSON.parse(localStorage.getItem(STORE) || '[]'); } catch (e) { return []; }
  }
  function save(record) {
    if (!CONFIG.storeLocally) return record;
    try {
      var all = readAll();
      all.push(record);
      localStorage.setItem(STORE, JSON.stringify(all.slice(-200)));
    } catch (e) {}
    return record;
  }

  /* --------------------------------------------------------- validation */
  var RULES = {
    email: {
      test: function (v) { return /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v.trim()); },
      msg: 'Enter a valid email address, e.g. name@example.com'
    },
    tel: {
      test: function (v) { return !v.trim() || /^[\d\s()+.-]{7,}$/.test(v.trim()); },
      msg: 'Enter a valid phone number'
    },
    number: {
      test: function (v) { return !v.trim() || !isNaN(parseFloat(v)); },
      msg: 'Enter a number'
    }
  };

  function fieldOf(input) { return input.closest('.field') || input.closest('.check') || input.parentElement; }

  function errorSlot(field) {
    // the slot usually lives inside .field; for checkbox labels it follows them
    var slot = $('.field-error', field);
    if (slot) return slot;
    var sib = field.nextElementSibling;
    while (sib) {
      if (sib.classList && sib.classList.contains('field-error')) return sib;
      if (sib.classList && (sib.classList.contains('check') || sib.classList.contains('field'))) break;
      sib = sib.nextElementSibling;
    }
    return null;
  }

  function setError(input, message) {
    var field = fieldOf(input);
    if (!field) return;
    field.classList.add('has-error');
    var slot = errorSlot(field);
    if (slot) { slot.textContent = message; slot.setAttribute('role', 'alert'); }
    input.setAttribute('aria-invalid', 'true');
  }
  function clearError(input) {
    var field = fieldOf(input);
    if (!field) return;
    field.classList.remove('has-error');
    var slot = errorSlot(field);
    if (slot && !$('.has-error', slot.parentElement)) slot.textContent = '';
    input.removeAttribute('aria-invalid');
  }

  function validateInput(input) {
    if (input.type === 'hidden' || input.disabled) return true;
    var value = input.value == null ? '' : String(input.value);
    var label = input.dataset.label || (input.labels && input.labels[0] ? input.labels[0].textContent.replace('*', '').trim() : 'This field');

    if (input.type === 'checkbox' && input.required && !input.checked) {
      setError(input, input.dataset.error || 'Please tick this box to continue');
      return false;
    }
    if (input.required && !value.trim()) {
      setError(input, input.dataset.error || label + ' is required');
      return false;
    }
    if (value.trim() && RULES[input.type] && !RULES[input.type].test(value)) {
      setError(input, RULES[input.type].msg);
      return false;
    }
    if (input.minLength > 0 && value.trim() && value.trim().length < input.minLength) {
      setError(input, label + ' should be at least ' + input.minLength + ' characters');
      return false;
    }
    if (input.type === 'number' && value.trim()) {
      var n = parseFloat(value);
      if (input.min !== '' && n < parseFloat(input.min)) { setError(input, 'Minimum is ' + input.min); return false; }
      if (input.max !== '' && n > parseFloat(input.max)) { setError(input, 'Maximum is ' + input.max); return false; }
    }
    clearError(input);
    return true;
  }

  function validateForm(form) {
    var ok = true, firstBad = null;
    $$('input, select, textarea', form).forEach(function (input) {
      if (input.name === '_hp') return;
      if (!validateInput(input)) { ok = false; if (!firstBad) firstBad = input; }
    });
    if (firstBad) {
      firstBad.focus({ preventScroll: true });
      firstBad.scrollIntoView({ block: 'center', behavior: window.Rootstock && window.Rootstock.reduced ? 'auto' : 'smooth' });
    }
    return ok;
  }

  /* ------------------------------------------------------------- submit */
  function collect(form) {
    var data = {};
    new FormData(form).forEach(function (value, key) {
      if (key === '_hp') return;
      if (data[key] !== undefined) {
        data[key] = [].concat(data[key], value);
      } else { data[key] = value; }
    });
    return data;
  }

  function showStatus(form, message, isError) {
    var box = $('[data-form-status]', form);
    if (!box) { if (window.Rootstock) window.Rootstock.toast(message); return; }
    box.textContent = message;
    box.classList.toggle('is-error', !!isError);
    box.classList.add('is-shown');
    if (!isError) setTimeout(function () { box.classList.remove('is-shown'); }, 9000);
  }

  function handle(form) {
    if (form.dataset.bound) return;
    form.dataset.bound = '1';
    form.setAttribute('novalidate', '');

    // live re-validation once a field has been marked
    $$('input, select, textarea', form).forEach(function (input) {
      var evt = (input.type === 'checkbox' || input.tagName === 'SELECT') ? 'change' : 'blur';
      input.addEventListener(evt, function () { if (input.value || input.required) validateInput(input); });
      input.addEventListener('input', function () {
        if (fieldOf(input) && fieldOf(input).classList.contains('has-error')) validateInput(input);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.elements._hp && form.elements._hp.value) return;   // honeypot: silently drop
      if (!validateForm(form)) {
        showStatus(form, 'Please check the highlighted fields and try again.', true);
        return;
      }
      var btn = $('[type="submit"]', form);
      if (btn) btn.classList.add('is-loading');

      var record = {
        type: form.dataset.capture || 'general',
        page: location.pathname.split('/').pop() || 'index.html',
        submittedAt: new Date().toISOString(),
        data: collect(form)
      };

      var finish = function (okMessage) {
        if (btn) btn.classList.remove('is-loading');
        save(record);
        form.dispatchEvent(new CustomEvent('rootstock:captured', { detail: record, bubbles: true }));
        var redirect = form.dataset.redirect;
        if (redirect) {
          var name = record.data.firstName || record.data.name || '';
          location.href = redirect + '?type=' + encodeURIComponent(record.type) +
            (name ? '&name=' + encodeURIComponent(name) : '');
          return;
        }
        form.reset();
        $$('.field.has-error', form).forEach(function (f) { f.classList.remove('has-error'); });
        showStatus(form, okMessage);
        if (window.Rootstock && !$('[data-form-status]', form)) window.Rootstock.toast(okMessage);
      };

      var done = form.dataset.success || 'Thank you — we have your details and will be in touch shortly.';

      if (CONFIG.endpoint) {
        fetch(CONFIG.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(record)
        }).then(function () { finish(done); })
          .catch(function () {
            if (btn) btn.classList.remove('is-loading');
            showStatus(form, 'We could not reach the server. Please try again, or email hello@rootstock.earth.', true);
          });
      } else {
        setTimeout(function () { finish(done); }, 620);   // simulated round-trip
      }
    });
  }

  /* ------------------------------------------------ donation calculator */
  var COST_PER_TREE = 3;         // £ — the cost of raising, planting and monitoring one tree
  var CO2_PER_TREE = 0.025;      // tonnes of CO₂e sequestered per tree over 20 years

  function money(n) {
    return '£' + n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  }

  function initDonation() {
    var form = $('[data-donation]');
    if (!form) return;
    var custom = $('[data-donation-custom]', form);
    var outAmount = $('[data-out="amount"]');
    var outTrees = $('[data-out="trees"]');
    var outCo2 = $('[data-out="co2"]');
    var outFreq = $('[data-out="frequency"]');
    var outAnnual = $('[data-out="annual"]');
    var outLabel = $('[data-out="label"]');

    function amount() {
      var checked = form.querySelector('input[name="amount"]:checked');
      if (checked && checked.value === 'custom') return parseFloat(custom.value) || 0;
      return checked ? parseFloat(checked.value) : 0;
    }
    function frequency() {
      var f = form.querySelector('input[name="frequency"]:checked');
      return f ? f.value : 'once';
    }
    function update() {
      var amt = amount();
      var freq = frequency();
      var trees = Math.floor(amt / COST_PER_TREE);
      if (outAmount) outAmount.textContent = money(amt);
      if (outTrees) outTrees.textContent = trees.toLocaleString();
      if (outCo2) outCo2.textContent = (trees * CO2_PER_TREE).toFixed(2);
      if (outFreq) outFreq.textContent = freq === 'monthly' ? 'every month' : 'one-off gift';
      if (outAnnual) outAnnual.textContent = money(freq === 'monthly' ? amt * 12 : amt);
      if (outLabel) outLabel.textContent = freq === 'monthly' ? 'Planted in your first year' : 'Trees funded';
      var hidden = form.querySelector('input[name="calculatedTrees"]');
      if (hidden) hidden.value = trees;
      var btn = $('[data-donation-submit]', form);
      if (btn) {
        btn.querySelector('[data-donation-btn-label]').textContent =
          amt > 0 ? 'Give ' + money(amt) + (freq === 'monthly' ? ' a month' : '') : 'Choose an amount';
        btn.disabled = amt <= 0;
      }
    }
    form.addEventListener('change', update);
    form.addEventListener('input', update);
    $$('input[name="amount"]', form).forEach(function (radio) {
      radio.addEventListener('change', function () {
        var isCustom = radio.value === 'custom';
        var wrap = $('[data-donation-custom-wrap]', form);
        if (wrap) wrap.hidden = !isCustom;
        if (isCustom && custom) custom.focus();
      });
    });
    update();
  }

  /* ------------------------------------------- thank-you page rendering */
  var COPY = {
    donation: { title: 'Your gift is planting trees', body: 'Your donation goes straight into seed collection, nursery care and three years of monitoring for every tree we put in the ground. A receipt is on its way to your inbox.' },
    newsletter: { title: 'You are on the list', body: 'Expect one email a month: what we planted, what survived, what we learned, and where the money went. Nothing else, ever.' },
    contact: { title: 'Message received', body: 'A real person reads every message. We reply within two working days — usually much sooner.' },
    volunteer: { title: 'Welcome to the crew', body: 'We will send you the next three planting weekends and everything you need to know before you arrive. Bring boots.' },
    partner: { title: 'Let us build something', body: 'Our partnerships lead will be in touch within two working days with a short call invitation and our impact prospectus.' },
    general: { title: 'Thank you', body: 'We have your details and will be in touch shortly.' }
  };

  function initThankYou() {
    var host = $('[data-thanks]');
    if (!host) return;
    var params = new URLSearchParams(location.search);
    var type = params.get('type') || 'general';
    var name = params.get('name');
    var copy = COPY[type] || COPY.general;
    var t = $('[data-thanks-title]', host);
    var b = $('[data-thanks-body]', host);
    var badge = $('[data-thanks-badge]', host);
    if (t) t.textContent = name ? copy.title.replace('Your', name + ', your').replace('You are', name + ', you are') : copy.title;
    if (b) b.textContent = copy.body;
    if (badge) badge.textContent = type.charAt(0).toUpperCase() + type.slice(1);

    var last = readAll().slice(-1)[0];
    var summary = $('[data-thanks-summary]');   // lives outside the banner host
    if (summary && last) {
      var rows = Object.keys(last.data).filter(function (k) {
        return k !== 'calculatedTrees' && String(last.data[k]).trim() !== '';
      });
      if (!rows.length) { summary.hidden = true; return; }
      summary.innerHTML = '<h3 class="h4">What you sent us</h3>' +
        '<div class="table-wrap mt-4"><table class="data"><tbody>' +
        rows.map(function (k) {
          var label = k.replace(/([A-Z])/g, ' $1').replace(/^./, function (s) { return s.toUpperCase(); });
          var val = String(last.data[k]);
          return '<tr><th scope="row">' + esc(label) + '</th><td>' + esc(val) + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    }
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* ---------------------------------------------------------------- boot */
  function boot() {
    $$('form[data-capture]').forEach(handle);
    initDonation();
    initThankYou();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  window.Rootstock = window.Rootstock || {};
  window.Rootstock.Forms = {
    config: CONFIG,
    leads: readAll,
    clear: function () { try { localStorage.removeItem(STORE); } catch (e) {} },
    export: function () { return JSON.stringify(readAll(), null, 2); },
    costPerTree: COST_PER_TREE
  };
})();
