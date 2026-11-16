// Ejecutar: node test/physics.test.js
'use strict';
const assert = require('assert');
globalThis.SM = {};
require('../js/data.js');
require('../js/physics.js');
const P = globalThis.SM.physics, D = globalThis.SM.data;
const earth = D.PLANETS.find(function (p) { return p.id === 'earth'; });
const mars = D.PLANETS.find(function (p) { return p.id === 'mars'; });
const jd = P.julianDate(new Date(Date.UTC(2026, 10, 14)));

const e = P.planetState(earth, jd);
assert(Math.hypot(e.x, e.y) > 0.98 && Math.hypot(e.x, e.y) < 1.02, 'Tierra ~1 UA');

const h = P.hohmann(1, 1.52371);
assert(Math.abs(h.days - 259) < 2, 'Tierra->Marte ~259 días');
assert(Math.abs(h.dvHelio / 1000 - 2.94) < 0.1, 'Δv heliocéntrico ~2.94 km/s');
assert(h.dvLEO / 1000 > 3.4 && h.dvLEO / 1000 < 3.8, 'Δv desde LEO ~3.6 km/s');

const q = P.transferPos(h, 10, h.days);
assert(Math.abs(q.r - 1.52371) < 0.01, 'llega a la órbita de Marte');
assert(Math.abs(P.wrap180(Math.atan2(q.y, q.x) * 180 / Math.PI - 190)) < 0.5, 'llega a 180° del punto de salida');

const w = P.nextWindow(earth, mars, jd), pw = P.plan(earth, mars, w);
assert(w >= jd && Math.abs(pw.err) <= 4, 'la ventana es futura y el error de llegada <= 4°');
console.log('OK. Mejor ventana a Marte:', new Date((w - 2440587.5) * 86400000).toISOString().slice(0, 10), 'error', pw.err.toFixed(2) + '°');

require('../js/glossary.js');
require('../js/learn.js');
assert.strictEqual(globalThis.SM.learn.sci(1.32712440018e20, 3), '1,327 × 10²⁰', 'notación científica');
assert.strictEqual(globalThis.SM.learn.sci(9.99999, 2), '10,00 × 10⁰'.replace('10,00 × 10⁰', '1,00 × 10¹'), 'redondeo a la siguiente potencia');
console.log('OK notación científica y glosario cargan');
