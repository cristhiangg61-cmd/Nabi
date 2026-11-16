// Minijuego de ascenso: sube el cohete hasta 100 km (línea de Kármán) sin quedarte sin combustible.
// Basado en el prototipo "Misión Marte 2D" del equipo; el empuje depende del lanzador elegido.
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});
  if (typeof document === 'undefined') return;
  const $ = function (id) { return document.getElementById(id); };
  const G = 0.05, ESC = 10000; // gravedad y altitud de escape (100 unidades = 1 km)
  let cv, cx, W, H, R, P, thrust = false, run = false, done = null, parts = [];

  function start(cb) {
    const m = SM.mission && SM.mission.cfg;
    if (!m) { cb(); return; }
    done = cb; $('ascent').classList.remove('hidden');
    cv = $('asc-canvas'); cx = cv.getContext('2d');
    const r = cv.getBoundingClientRect(); W = cv.width = r.width; H = cv.height = r.height;
    R = { x: W / 2, y: H - 100, vy: 0, fuel: 100, alt: 0 }; P = m.l.twr; parts = [];
    $('asc-retry').classList.add('hidden'); $('asc-msg').textContent = 'Mantén Espacio (o el botón) para despegar.';
    run = true; requestAnimationFrame(loop);
  }

  function fire() {
    parts.push({ x: R.x + Math.random() * 10 - 5, y: R.y + 30, vx: Math.random() * 2 - 1, vy: Math.random() * 5 + 5, l: 100, c: Math.random() > 0.5 ? '#f97316' : '#eab308', s: Math.random() * 6 + 4 });
    parts.push({ x: R.x + Math.random() * 20 - 10, y: R.y + 40, vx: Math.random() * 2 - 1, vy: Math.random() * 3 + 2, l: 150, c: '#64748b', s: Math.random() * 10 + 5 });
  }

  function loop() {
    if (!run) return;
    R.vy += G;
    if (thrust && R.fuel > 0) { R.vy -= P; R.fuel -= 0.1; fire(); }
    R.y += R.vy;
    const ty = H * 0.6;
    if (R.y < ty) { const d = ty - R.y; R.alt += d; R.y = ty; parts.forEach(function (p) { p.y += d; }); }
    if (R.y > H - 100) { R.y = H - 100; R.vy = 0; }
    parts.forEach(function (p) { p.x += p.vx; p.y += p.vy; p.l -= 2; });
    parts = parts.filter(function (p) { return p.l > 0; });
    $('asc-alt').textContent = Math.floor(R.alt / 100) + ' km'; $('asc-fuel').value = Math.max(0, R.fuel);
    draw();
    if (R.alt > ESC) return end(true);
    if (R.fuel <= 0 && R.vy >= 0) return end(false); // sin combustible y cayendo
    requestAnimationFrame(loop);
  }

  function end(ok) {
    run = false; thrust = false;
    if (ok) {
      SM.mission.cfg.ascentFuel = Math.max(0, R.fuel) / 100;
      $('asc-msg').textContent = '¡Órbita alcanzada! Combustible sobrante: ' + Math.round(R.fuel) + ' %';
      setTimeout(function () { $('ascent').classList.add('hidden'); done(); }, 1500);
    } else {
      $('asc-msg').textContent = 'Te quedaste sin combustible antes de los 100 km. Empuja en tramos largos y no malgastes.';
      $('asc-retry').classList.remove('hidden');
    }
  }

  function tri(a, b, c, d, e, f) { cx.beginPath(); cx.moveTo(a, b); cx.lineTo(c, d); cx.lineTo(e, f); cx.fill(); }

  function draw() {
    const p = Math.min(R.alt / ESC, 1);
    cx.fillStyle = 'rgb(' + (135 * (1 - p) | 0) + ',' + (206 * (1 - p) | 0) + ',' + ((235 * (1 - p) + 20 * p) | 0) + ')'; cx.fillRect(0, 0, W, H);
    if (p > 0.3) { cx.fillStyle = 'rgba(255,255,255,' + (p - 0.3) * 1.5 + ')'; for (let i = 0; i < 50; i++) { cx.beginPath(); cx.arc((Math.sin(i * 123) * 0.5 + 0.5) * W, (Math.cos(i * 321) * 0.5 + 0.5) * H, (i % 3) * 0.5 + 0.5, 0, 7); cx.fill(); } }
    const gy = H - 100 + R.alt * 0.5;
    if (gy < H) { cx.fillStyle = '#166534'; cx.fillRect(0, gy, W, H - gy); cx.fillStyle = '#475569'; cx.fillRect(W / 2 - 40, gy - 10, 80, 10); }
    parts.forEach(function (q) { cx.globalAlpha = q.l / 150; cx.fillStyle = q.c; cx.beginPath(); cx.arc(q.x, q.y, q.s, 0, 7); cx.fill(); });
    cx.globalAlpha = 1; cx.save(); cx.translate(R.x, R.y);
    cx.fillStyle = '#e2e8f0'; cx.fillRect(-15, -30, 30, 60);
    cx.fillStyle = '#ef4444'; tri(-15, -30, 15, -30, 0, -55); tri(-15, 30, -30, 40, -15, 15); tri(15, 30, 30, 40, 15, 15);
    cx.fillStyle = '#38bdf8'; cx.beginPath(); cx.arc(0, -10, 6, 0, 7); cx.fill(); cx.restore();
  }

  const on = function () { if (run) thrust = true; }, off = function () { thrust = false; };
  window.addEventListener('keydown', function (e) { if (e.code === 'Space' && run) { e.preventDefault(); thrust = true; } });
  window.addEventListener('keyup', function (e) { if (e.code === 'Space') off(); });
  ['mousedown', 'touchstart'].forEach(function (n) { $('asc-thrust').addEventListener(n, function (e) { e.preventDefault(); on(); }); });
  ['mouseup', 'mouseleave', 'touchend'].forEach(function (n) { $('asc-thrust').addEventListener(n, off); });
  $('asc-retry').addEventListener('click', function () { start(done); });
  $('asc-exit').addEventListener('click', function () { run = false; $('ascent').classList.add('hidden'); });
  SM.ascent = { start: start };
})();
