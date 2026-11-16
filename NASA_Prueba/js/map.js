// Mapa 2D del sistema solar en canvas. Recibe una "escena" y la dibuja; no calcula física.
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});
  const P = SM.physics;

  function create(canvas) {
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0;

    function fit() {
      const r = canvas.getBoundingClientRect(), d = window.devicePixelRatio || 1;
      if (Math.abs(r.width - W) < 1 && Math.abs(r.height - H) < 1) return;
      W = r.width; H = r.height;
      canvas.width = Math.round(W * d); canvas.height = Math.round(H * d);
      ctx.setTransform(d, 0, 0, d, 0, 0);
    }

    function line(pts, X, Y) {
      ctx.beginPath();
      pts.forEach(function (q, i) { if (i) ctx.lineTo(X(q.x), Y(q.y)); else ctx.moveTo(X(q.x), Y(q.y)); });
    }

    function draw(s) {
      fit();
      const k = (Math.min(W, H) / 2) * 0.9 / s.viewR;
      const X = function (x) { return W / 2 + x * k; };
      const Y = function (y) { return H / 2 - y * k; };
      ctx.clearRect(0, 0, W, H);
      ctx.lineWidth = 1;

      s.planets.forEach(function (p) {
        const st = P.planetState(p, s.jd);
        if (st.a > s.viewR * 1.02) return;
        line(P.orbitPoints(p, s.jd, 180), X, Y);
        ctx.strokeStyle = p.id === s.destId ? 'rgba(94,234,212,.55)' : 'rgba(142,151,189,.25)';
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(X(st.x), Y(st.y), p.id === s.destId ? 6 : 4, 0, 7);
        ctx.fillStyle = p.color; ctx.fill();
        ctx.fillStyle = '#8e97bd'; ctx.font = '12px system-ui,sans-serif';
        ctx.fillText(p.name, X(st.x) + 9, Y(st.y) - 7);
      });

      ctx.beginPath(); ctx.arc(W / 2, H / 2, 7, 0, 7); ctx.fillStyle = '#ffd36b'; ctx.fill();

      if (s.path) { ctx.setLineDash([5, 5]); line(s.path, X, Y); ctx.strokeStyle = 'rgba(255,179,71,.6)'; ctx.stroke(); ctx.setLineDash([]); }
      if (s.ghost) { // dónde estará el planeta destino cuando llegue el cohete
        ctx.beginPath(); ctx.arc(X(s.ghost.x), Y(s.ghost.y), 10, 0, 7); ctx.strokeStyle = '#5eead4'; ctx.stroke();
      }
      if (s.trail && s.trail.length > 1) { line(s.trail, X, Y); ctx.strokeStyle = '#ffb347'; ctx.lineWidth = 2; ctx.stroke(); ctx.lineWidth = 1; }
      if (s.rocket) { ctx.beginPath(); ctx.arc(X(s.rocket.x), Y(s.rocket.y), 4, 0, 7); ctx.fillStyle = '#fff'; ctx.fill(); }
    }

    return { draw: draw };
  }

  SM.map = { create: create };
})();
