// Interfaz del minijuego 1: transferencia interplanetaria. Conecta UI, física y mapa.
(function () {
  'use strict';
  const SM = globalThis.SM, P = SM.physics, PLANETS = SM.data.PLANETS, TOL = 4; // tolerancia de llegada (°)
  const earth = PLANETS.find(function (p) { return p.id === 'earth'; });
  const $ = function (id) { return document.getElementById(id); };
  const map = SM.map.create($('map'));
  const state = { jd: 0, dest: 'mars', flight: null, plan: null };

  const jdToIso = function (jd) { return new Date((jd - 2440587.5) * 86400000).toISOString().slice(0, 10); };
  const isoToJd = function (s) { return Date.parse(s + 'T00:00:00Z') / 86400000 + 2440587.5; };
  const destObj = function () { return PLANETS.find(function (p) { return p.id === state.dest; }); };

  function replan() {
    const d = destObj(), pl = P.plan(earth, d, state.jd), path = [];
    for (let i = 0; i <= 120; i++) path.push(P.transferPos(pl.h, pl.theta0, (pl.h.days * i) / 120));
    const dv = P.rocketDv(+$('isp').value, +$('dry').value, +$('prop').value, +$('pay').value);
    state.plan = { dest: d, h: pl.h, err: pl.err, theta0: pl.theta0, arrival: pl.arrival, path: path, dv: dv };
    $('r-dv').textContent = (dv / 1000).toFixed(1) + ' / ' + (pl.h.dvTotal / 1000).toFixed(1) + ' km/s';
    $('r-days').textContent = Math.round(pl.h.days) + ' días';
    $('r-win').textContent = (Math.abs(pl.err) <= TOL ? 'Abierta' : 'Cerrada') + ' (' + pl.err.toFixed(1) + '°)';
    SM.learn.update(state.plan, { isp: +$('isp').value, dry: +$('dry').value, prop: +$('prop').value, pay: +$('pay').value }, TOL);
  }

  function render() {
    const pl = state.plan, f = state.flight, t = f ? f.t : 0;
    const k = f ? Math.min(120, Math.floor((120 * t) / pl.h.days)) : 0;
    map.draw({
      jd: state.jd + t, planets: PLANETS, destId: pl.dest.id, viewR: Math.max(1.4, pl.h.rMax * 1.15),
      path: pl.path, ghost: pl.arrival, trail: f ? pl.path.slice(0, k + 1) : null,
      rocket: f ? P.transferPos(pl.h, pl.theta0, t) : null
    });
    $('hud').textContent = f ? 'Día ' + Math.round(t) + ' de ' + Math.round(pl.h.days) : 'Fecha: ' + jdToIso(state.jd);
  }

  function refresh() { state.flight = null; $('msg').textContent = ''; replan(); render(); }

  function tick(now) {
    const f = state.flight, pl = state.plan;
    if (!f || f.done) return;
    f.t = Math.min(pl.h.days, ((now - f.t0) / 1000) * (pl.h.days / 8)); // el viaje dura ~8 s en pantalla
    render();
    if (f.t < pl.h.days) { requestAnimationFrame(tick); return; }
    f.done = true;
    const err = Math.abs(pl.err);
    $('msg').textContent = SM.learn.result(err <= TOL, pl.err, pl);
    if (SM.mission) SM.mission.finish(err <= TOL, pl);
  }

  function launch() {
    replan();
    const pl = state.plan;
    if (pl.dv < pl.h.dvTotal) {
      $('msg').textContent = 'Combustible insuficiente: faltan ' + ((pl.h.dvTotal - pl.dv) / 1000).toFixed(1) + ' km/s. Agranda el tanque (propelente) o usa un motor con más Isp.';
      return;
    }
    $('msg').textContent = '';
    const go = function () { state.flight = { t: 0, t0: performance.now(), done: false }; requestAnimationFrame(tick); };
    if (SM.ascent) SM.ascent.start(go); else go(); // primero el ascenso, luego el viaje por nuestras órbitas
  }

  function setDate(jd) { state.jd = jd; $('date').value = jdToIso(jd); refresh(); }

  PLANETS.filter(function (p) { return p.id !== 'earth'; }).forEach(function (p) {
    const o = document.createElement('option'); o.value = p.id; o.textContent = p.name; $('dest').appendChild(o);
  });
  $('dest').value = state.dest;
  $('dest').addEventListener('change', function (e) { state.dest = e.target.value; refresh(); });
  $('date').addEventListener('change', function (e) { if (e.target.value) setDate(isoToJd(e.target.value)); });
  $('prev').addEventListener('click', function () { setDate(state.jd - 30); });
  $('next').addEventListener('click', function () { setDate(state.jd + 30); });
  $('window').addEventListener('click', function () { setDate(Math.round(P.nextWindow(earth, destObj(), state.jd) - 0.5) + 0.5); });
  ['isp', 'dry', 'prop', 'pay'].forEach(function (id) { $(id).addEventListener('input', refresh); });
  $('launch').addEventListener('click', launch);
  window.addEventListener('resize', render);

  $('apod').addEventListener('click', async function () {
    const box = $('apodbox'); box.textContent = 'Cargando…';
    try {
      const d = await SM.api.apod();
      box.textContent = '';
      const t = document.createElement('p'); t.textContent = d.title; box.appendChild(t);
      if (d.media_type === 'image') { const i = document.createElement('img'); i.src = d.url; i.alt = d.title; box.appendChild(i); }
    } catch (e) { box.textContent = 'No se pudo conectar con la API de NASA (' + e.message + '). Revisa la clave en js/config.js.'; }
  });

  // Arranca en la primera ventana abierta al destino por defecto, para que el primer lanzamiento sí funcione.
  setDate(P.nextWindow(earth, destObj(), isoToJd(jdToIso(P.julianDate(new Date())))));
})();
