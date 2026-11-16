// Diseño de misión: catálogos, constructor, puntuación con eventos aleatorios y reporte final.
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});
  const BUDGET = 300; // M$ (millones de dólares)
  const OBJ = [
    { id: 'mars', name: 'Rover en Marte', dest: 'mars', pts: 100 },
    { id: 'venus', name: 'Orbitador de Venus', dest: 'venus', pts: 80 },
    { id: 'jupiter', name: 'Sonda a Júpiter', dest: 'jupiter', pts: 160 }
  ];
  const INS = [ // t = masa (t), kw = consumo, cost = M$, pts = ciencia
    { id: 'cam', name: 'Cámara', t: 0.5, kw: 0.3, cost: 20, pts: 20 },
    { id: 'spec', name: 'Espectrómetro', t: 1, kw: 0.8, cost: 45, pts: 40 },
    { id: 'radar', name: 'Radar', t: 2, kw: 2, cost: 80, pts: 55 },
    { id: 'mag', name: 'Magnetómetro', t: 0.3, kw: 0.1, cost: 15, pts: 12 }
  ];
  const LAU = [ // cap = masa máxima de carga (t); twr = empuje del minijuego de ascenso
    { id: 'small', name: 'Ligero', isp: 350, dry: 12, prop: 250, cap: 3, cost: 60, twr: 0.08 },
    { id: 'mid', name: 'Mediano', isp: 450, dry: 20, prop: 500, cap: 6, cost: 120, twr: 0.12 },
    { id: 'heavy', name: 'Pesado', isp: 460, dry: 35, prop: 1500, cap: 12, cost: 250, twr: 0.16 }
  ];
  const PWR = [
    { id: 'solar', name: 'Paneles solares', t: 0.4, cost: 15, kw: 4, solar: true },
    { id: 'rtg', name: 'RTG (nuclear)', t: 0.9, cost: 60, kw: 2, solar: false }
  ];
  const COM = [ // gain: la señal útil baja con la distancia (gain / UA)
    { id: 'sm', name: 'Antena pequeña', t: 0.2, cost: 10, gain: 2 },
    { id: 'lg', name: 'Antena grande', t: 0.6, cost: 35, gain: 6 }
  ];
  const sel = { obj: 'mars', lau: 'mid', pwr: 'solar', com: 'sm', ins: { cam: true, spec: true } };
  const by = function (a, id) { return a.find(function (x) { return x.id === id; }); };
  let cfg = null;

  function calc() {
    const k = { o: by(OBJ, sel.obj), l: by(LAU, sel.lau), p: by(PWR, sel.pwr), c: by(COM, sel.com) };
    k.ins = INS.filter(function (i) { return sel.ins[i.id]; });
    k.mass = k.ins.reduce(function (a, i) { return a + i.t; }, 0) + k.p.t + k.c.t;
    k.cost = k.l.cost + k.p.cost + k.c.cost + k.ins.reduce(function (a, i) { return a + i.cost; }, 0);
    return k;
  }

  function finish(ok, pl) {
    if (!cfg) return;
    const k = cfg, r = pl.dest.el[0][0], L = [];
    if (!ok) return report('Misión fallida', ['Llegaste cuando ' + pl.dest.name + ' ya no estaba en ese punto de su órbita: la ventana de lanzamiento importa.', 'Puntuación: 0 pts.']);
    const need = k.ins.reduce(function (a, i) { return a + i.kw; }, 0), power = k.p.solar ? k.p.kw / (r * r) : k.p.kw;
    let pF = Math.min(1, power / need), cF = Math.min(1, k.c.gain / r), eF = 1;
    L.push('Energía en ' + pl.dest.name + ': ' + power.toFixed(2) + ' kW disponibles y ' + need.toFixed(1) + ' kW necesarios, así que trabaja el ' + Math.round(pF * 100) + ' % de los instrumentos.' + (k.p.solar ? ' (La luz del Sol baja con 1/r²).' : ''));
    L.push('Comunicaciones: ' + k.c.name + ' a ' + r.toFixed(2) + ' UA, llega el ' + Math.round(cF * 100) + ' % de los datos.');
    for (let t = 1; t <= 3; t++) {
      const x = Math.random();
      if (x < 0.2) { if (k.p.solar) { pF *= 0.7; L.push('Turno ' + t + ': tormenta solar, los paneles pierden 30 % de energía.'); } else L.push('Turno ' + t + ': tormenta solar, pero el RTG no depende del Sol: sin daños.'); }
      else if (x < 0.4) { cF *= k.c.gain > 3 ? 0.9 : 0.6; L.push('Turno ' + t + ': falla de antena. ' + (k.c.gain > 3 ? 'La antena grande tiene redundancia (−10 %).' : 'La antena pequeña pierde 40 % de los datos.')); }
      else if (x < 0.5) { eF *= 0.9; L.push('Turno ' + t + ': impacto de micrometeoroide (−10 %).'); }
      else L.push('Turno ' + t + ': operación normal.');
    }
    const base = k.o.pts + k.ins.reduce(function (a, i) { return a + i.pts; }, 0), bonus = 1 + 0.2 * k.ascentFuel;
    const score = Math.round(base * pF * cF * eF * bonus);
    L.push('Ciencia base ' + base + ' pts × energía ' + pF.toFixed(2) + ' × comunicaciones ' + cF.toFixed(2) + ' × eventos ' + eF.toFixed(2) + ' × bono de ascenso ' + bonus.toFixed(2) + '.');
    L.push('Puntuación final: ' + score + ' pts, ' + (score / k.cost).toFixed(2) + ' pts por millón de dólares (' + k.cost + ' M$).');
    report(score >= 0.6 * base ? '¡Misión exitosa!' : 'Misión con pérdidas', L);
  }

  if (typeof document === 'undefined') { SM.mission = { finish: finish, calc: calc }; return; }
  const $ = function (id) { return document.getElementById(id); };
  const el = function (t, s, p, c) { const x = document.createElement(t); if (s) x.textContent = s; if (c) x.className = c; p.appendChild(x); return x; };

  function report(title, L) {
    $('rp-title').textContent = title; const ul = $('rp-list'); ul.textContent = '';
    L.forEach(function (s) { el('li', s, ul); });
    if (!$('report').open) $('report').showModal();
  }

  function summary() {
    const k = calc(), P = SM.physics, d = SM.data.PLANETS.find(function (x) { return x.id === k.o.dest; });
    const h = P.hohmann(1, d.el[0][0]), dv = P.rocketDv(k.l.isp, k.l.dry, k.l.prop, k.mass), errs = [], ul = $('b-sum');
    if (!k.ins.length) errs.push('Elige al menos un instrumento.');
    if (k.mass > k.l.cap) errs.push('Te pasas de masa: ' + k.mass.toFixed(1) + ' t > ' + k.l.cap + ' t. El cohete no despegaría.');
    if (k.cost > BUDGET) errs.push('Te pasas del presupuesto: ' + k.cost + ' M$ > ' + BUDGET + ' M$.');
    ul.textContent = '';
    el('li', 'Masa de la carga: ' + k.mass.toFixed(1) + ' t (el cohete soporta ' + k.l.cap + ' t)', ul);
    el('li', 'Costo: ' + k.cost + ' M$ de ' + BUDGET + ' M$', ul);
    el('li', 'Δv: ' + (dv / 1000).toFixed(1) + ' km/s disponibles y ' + (h.dvTotal / 1000).toFixed(1) + ' necesarios ' + (dv >= h.dvTotal ? '✓' : '✗ (elige otro lanzador o menos masa)'), ul);
    $('b-err').textContent = errs.join(' '); $('b-go').disabled = errs.length > 0;
  }

  function build() {
    const b = $('builder'); b.textContent = '';
    el('h2', 'Diseña tu misión', b); el('p', 'Masa, dinero y energía son limitados: elige con cuidado.', b);
    [['obj', 'Objetivo', OBJ, function (o) { return ' · ' + o.pts + ' pts'; }], ['lau', 'Lanzador', LAU, function (o) { return ' · ' + o.cost + ' M$, carga ≤ ' + o.cap + ' t'; }],
      ['pwr', 'Energía', PWR, function (o) { return ' · ' + o.t + ' t, ' + o.cost + ' M$'; }], ['com', 'Comunicaciones', COM, function (o) { return ' · ' + o.t + ' t, ' + o.cost + ' M$'; }]].forEach(function (f) {
      const lab = el('label', '', b), sp = el('span', f[1] + ' ', lab), s = el('select', '', lab);
      if (f[0] === 'pwr') { const t = el('button', '?', sp, 'term'); t.type = 'button'; t.dataset.term = 'rtg'; }
      f[2].forEach(function (o) { el('option', o.name + f[3](o), s).value = o.id; });
      s.value = sel[f[0]]; s.addEventListener('change', function () { sel[f[0]] = s.value; summary(); });
    });
    const fs = el('fieldset', '', b); el('legend', 'Instrumentos', fs);
    INS.forEach(function (i) {
      const lab = el('label', '', fs), cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!sel.ins[i.id];
      cb.addEventListener('change', function () { sel.ins[i.id] = cb.checked; summary(); });
      el('span', i.name + ' · ' + i.t + ' t · ' + i.kw + ' kW · ' + i.cost + ' M$ · ' + i.pts + ' pts', lab); lab.appendChild(cb);
    });
    el('ul', '', b).id = 'b-sum'; el('p', '', b).id = 'b-err';
    const go = el('button', 'Listo para lanzar', b, 'primary'); go.id = 'b-go'; go.type = 'button'; go.addEventListener('click', apply);
    summary();
  }

  function apply() {
    const k = calc(); k.ascentFuel = 0.3; cfg = k;
    const set = function (id, v, ev) { $(id).value = v; $(id).dispatchEvent(new Event(ev)); };
    set('isp', k.l.isp, 'input'); set('dry', k.l.dry, 'input'); set('prop', k.l.prop, 'input'); set('pay', k.mass.toFixed(1), 'input'); set('dest', k.o.dest, 'change');
    document.body.dataset.built = '1'; $('builder').classList.add('hidden');
  }

  SM.mission = { finish: finish, calc: calc, get cfg() { return cfg; } };
  build(); $('builder').classList.remove('hidden');
  $('open-builder').addEventListener('click', function () { build(); $('builder').classList.remove('hidden'); });
  $('rp-close').addEventListener('click', function () { $('report').close(); });
})();
