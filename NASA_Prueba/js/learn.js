// Capa educativa: modo Explorador/Ingeniero, pistas, medidor, cálculo paso a paso y glosario.
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});
  const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
  const n = function (x, d) { return x.toFixed(d).replace('.', ','); };
  let last = null, mode = 'explorer';

  function sci(x, d) {
    if (!x || !isFinite(x)) return '0';
    let e = Math.floor(Math.log10(Math.abs(x))), m = x / Math.pow(10, e);
    if (+m.toFixed(d) >= 10) { m /= 10; e += 1; }
    return n(m, d) + ' × 10' + String(e).split('').map(function (c) { return SUP[c]; }).join('');
  }

  function steps(pl, rk, kids) {
    const C = SM.data.CONST, h = pl.h, nm = pl.dest.name, ok = pl.dv >= h.dvTotal;
    const kmh = function (v) { return Math.round(v * 3600).toLocaleString('es-CO'); };
    if (kids) return [
      'Tu cohete puede cambiar su velocidad hasta ' + n(pl.dv / 1000, 1) + ' km/s (¡unos ' + kmh(pl.dv / 1000) + ' km/h!).',
      'Para llegar a ' + nm + ' necesita ' + n(h.dvTotal / 1000, 1) + ' km/s. ' + (ok ? 'Le alcanza.' : 'Todavía le falta.'),
      'El viaje dura ' + Math.round(h.days) + ' días, unos ' + n(h.days / 30.4, 1) + ' meses.',
      'Hay que salir cuando ' + nm + ' vaya a estar en el lugar de llegada: esa es la ventana de lanzamiento.'
    ];
    const m0 = rk.dry + rk.prop + rk.pay, mf = rk.dry + rk.pay, a = h.aT * C.AU;
    return [
      'm₀ = masa seca + propelente + carga = ' + rk.dry + ' + ' + rk.prop + ' + ' + rk.pay + ' = ' + m0 + ' t = ' + sci(m0 * 1000, 2) + ' kg.',
      'm_f = masa seca + carga = ' + mf + ' t = ' + sci(mf * 1000, 2) + ' kg.',
      'Tsiolkovsky: Δv = Isp · g₀ · ln(m₀/m_f) = ' + rk.isp + ' s × ' + n(C.G0, 5) + ' m/s² × ln(' + n(m0 / mf, 2) + ') = ' + sci(pl.dv, 2) + ' m/s = ' + n(pl.dv / 1000, 2) + ' km/s (' + kmh(pl.dv / 1000) + ' km/h).',
      'Δv necesario = ascenso ' + n(C.ASCENT_DV / 1000, 1) + ' km/s + salida desde LEO ' + n(h.dvLEO / 1000, 2) + ' km/s = ' + n(h.dvTotal / 1000, 2) + ' km/s (de la salida, ' + n(h.dvHelio / 1000, 2) + ' km/s son cambio de velocidad respecto al Sol).',
      'Hohmann: a = (r₁ + r₂)/2 = ' + n(h.aT, 3) + ' UA = ' + sci(a, 3) + ' m (1 UA = ' + sci(C.AU, 3) + ' m). t = π·√(a³/GM☉), con GM☉ = ' + sci(C.GM_SUN, 3) + ' m³/s², da t = ' + sci(h.days * 86400, 3) + ' s = ' + Math.round(h.days) + ' días.',
      ok ? 'Resultado: ' + n(pl.dv / 1000, 2) + ' ≥ ' + n(h.dvTotal / 1000, 2) + ' km/s → el combustible alcanza.' : 'Resultado: faltan ' + n((h.dvTotal - pl.dv) / 1000, 2) + ' km/s → el combustible no alcanza.'
    ];
  }

  function result(ok, err, pl) {
    const nm = pl.dest.name, d = Math.round(pl.h.days);
    if (mode === 'explorer') return ok ? '¡Llegaste a ' + nm + '! 🎉 Tu cohete tardó ' + d + ' días.' : 'Casi... ' + nm + ' ya se había movido a otro lugar. Pulsa «Mejor ventana» e inténtalo otra vez.';
    return ok ? '¡Llegaste a ' + nm + '! Error de llegada: ' + n(Math.abs(err), 1) + '°. Vuelo de ' + d + ' días.' : 'Misión fallida: pasaste a ' + n(Math.abs(err), 1) + '° de ' + nm + '. Usa "Mejor ventana" y vuelve a lanzar.';
  }

  function update(pl, rk, tol) {
    last = { pl: pl, rk: rk, tol: tol };
    const pct = Math.min(100, Math.round((100 * pl.dv) / pl.h.dvTotal)), $ = function (id) { return document.getElementById(id); };
    $('gauge').value = pct;
    $('gauge-label').textContent = 'Combustible: ' + pct + ' % de lo necesario';
    $('tank-out').textContent = $('tank').value + ' de 10';
    const eng = mode === 'engineer', e = n(Math.abs(pl.err), 1);
    $('hint').textContent = Math.abs(pl.err) > tol
      ? 'La ventana está cerrada: ' + pl.dest.name + ' no estará donde llegue tu cohete. Pulsa «Mejor ventana».' + (eng ? ' (error ' + e + '° > ' + tol + '°)' : '')
      : pl.dv < pl.h.dvTotal ? 'Falta empuje. ' + (eng ? 'Sube el propelente o el Isp.' : 'Agranda el tanque.')
        : '¡Todo listo! Pulsa «Lanzar».';
    const ol = $('steps'); ol.textContent = '';
    steps(pl, rk, !eng).forEach(function (s) { const li = document.createElement('li'); li.textContent = s; ol.appendChild(li); });
  }

  function el(tag, text, parent) { const x = document.createElement(tag); x.textContent = text; parent.appendChild(x); return x; }

  function openGlossary(id) {
    const G = SM.glossary, body = document.getElementById('gl-body'), dlg = document.getElementById('glossary');
    body.textContent = '';
    const ids = id ? [id] : Object.keys(G), root = id ? body : el('dl', '', body);
    ids.forEach(function (k) {
      const t = G[k], box = id ? el('div', '', body) : root;
      if (id) { el('h3', t.s + ' · ' + t.es, box); el('p', 'Idioma original: ' + t.en + ' (' + t.o + ')', box); el('p', 'En fácil: ' + t.k, box); el('p', 'Técnico: ' + t.t, box); }
      else { el('dt', t.s + ' · ' + t.es + ' / ' + t.en, box); el('dd', mode === 'explorer' ? t.k : t.t, box); }
    });
    if (id) el('button', 'Ver todo el glosario', body).addEventListener('click', function () { openGlossary(); });
    if (!dlg.open) dlg.showModal();
  }

  function setMode(m) {
    mode = m; document.body.dataset.mode = m;
    document.getElementById('m-kid').setAttribute('aria-pressed', m === 'explorer');
    document.getElementById('m-eng').setAttribute('aria-pressed', m === 'engineer');
    if (last) update(last.pl, last.rk, last.tol);
  }

  SM.learn = { sci: sci, update: update, result: result };

  if (typeof document !== 'undefined') {
    const $ = function (id) { return document.getElementById(id); };
    $('m-kid').addEventListener('click', function () { setMode('explorer'); });
    $('m-eng').addEventListener('click', function () { setMode('engineer'); });
    $('tank').addEventListener('input', function () { $('prop').value = $('tank').value * 100; $('prop').dispatchEvent(new Event('input')); });
    $('gl-all').addEventListener('click', function () { openGlossary(); });
    $('gl-close').addEventListener('click', function () { $('glossary').close(); });
    document.addEventListener('click', function (e) { const b = e.target.closest('[data-term]'); if (b) openGlossary(b.dataset.term); });
  }
})();
