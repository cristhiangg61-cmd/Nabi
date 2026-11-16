// Física del prototipo: Kepler (posiciones), Hohmann (transferencia) y Tsiolkovsky (cohete). Sin DOM: se puede probar con Node.
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});
  const C = SM.data.CONST;
  const D2R = Math.PI / 180;

  function julianDate(date) { return date.getTime() / 86400000 + 2440587.5; }
  function wrap180(x) { return ((((x + 180) % 360) + 360) % 360) - 180; }

  function solveKepler(Mdeg, e) { // devuelve E en radianes
    const M = wrap180(Mdeg) * D2R;
    let E = M + e * Math.sin(M);
    for (let i = 0; i < 50; i++) {
      const dE = (M - (E - e * Math.sin(E))) / (1 - e * Math.cos(E));
      E += dE;
      if (Math.abs(dE) < 1e-10) break;
    }
    return E;
  }

  function currentElements(p, jd) {
    const T = (jd - 2451545.0) / 36525;
    return p.el.map(function (pair) { return pair[0] + pair[1] * T; });
  }

  function toEcliptic(el, E) {
    const a = el[0], e = el[1], inc = el[2] * D2R, peri = el[4], node = el[5];
    const w = (peri - node) * D2R, Om = node * D2R;
    const xp = a * (Math.cos(E) - e), yp = a * Math.sqrt(1 - e * e) * Math.sin(E);
    const cw = Math.cos(w), sw = Math.sin(w), cO = Math.cos(Om), sO = Math.sin(Om), ci = Math.cos(inc), si = Math.sin(inc);
    return {
      x: (cw * cO - sw * sO * ci) * xp + (-sw * cO - cw * sO * ci) * yp,
      y: (cw * sO + sw * cO * ci) * xp + (-sw * sO + cw * cO * ci) * yp,
      z: (sw * si) * xp + (cw * si) * yp
    };
  }

  function planetState(p, jd) {
    const el = currentElements(p, jd);
    const q = toEcliptic(el, solveKepler(el[3] - el[4], el[1]));
    return { x: q.x, y: q.y, z: q.z, a: el[0], e: el[1], lon: Math.atan2(q.y, q.x) / D2R };
  }

  function orbitPoints(p, jd, n) {
    const el = currentElements(p, jd), pts = [];
    for (let i = 0; i <= n; i++) pts.push(toEcliptic(el, (2 * Math.PI * i) / n));
    return pts;
  }

  // Transferencia de Hohmann circular-coplanar desde r1 hasta r2 (UA) + Δv desde LEO.
  function hohmann(r1AU, r2AU) {
    const r1 = r1AU * C.AU, r2 = r2AU * C.AU, at = (r1 + r2) / 2;
    const days = (Math.PI * Math.sqrt(Math.pow(at, 3) / C.GM_SUN)) / 86400;
    const v1 = Math.sqrt(C.GM_SUN / r1);
    const dvHelio = Math.abs(v1 * (Math.sqrt((2 * r2) / (r1 + r2)) - 1));
    const rl = C.R_EARTH + C.LEO_ALT;
    const dvLEO = Math.sqrt(dvHelio * dvHelio + (2 * C.MU_EARTH) / rl) - Math.sqrt(C.MU_EARTH / rl);
    return { days: days, dvHelio: dvHelio, dvLEO: dvLEO, dvTotal: C.ASCENT_DV + dvLEO, aT: at / C.AU, e: Math.abs(r2 - r1) / (r1 + r2), outward: r2 > r1, rMax: Math.max(r1AU, r2AU) };
  }

  function rocketDv(isp, mDry, mProp, payload) { // Tsiolkovsky, m/s
    return isp * C.G0 * Math.log((mDry + mProp + payload) / (mDry + payload));
  }

  // Posición del cohete (UA, ecliptica 2D) tDays después de salir de la Tierra en la longitud theta0 (°).
  function transferPos(h, theta0, tDays) {
    const n = 360 / (365.25 * Math.pow(h.aT, 1.5));
    const E = solveKepler((h.outward ? 0 : 180) + n * tDays, h.e);
    const nu = 2 * Math.atan2(Math.sqrt(1 + h.e) * Math.sin(E / 2), Math.sqrt(1 - h.e) * Math.cos(E / 2));
    const r = h.aT * (1 - h.e * Math.cos(E));
    const th = (theta0 + (h.outward ? 0 : 180)) * D2R + nu;
    return { x: r * Math.cos(th), y: r * Math.sin(th), r: r };
  }

  // Plan para lanzar en jd: error angular (°) entre donde llega el cohete y donde estará el planeta.
  function plan(earth, dest, jd) {
    const sE = planetState(earth, jd), sD0 = planetState(dest, jd);
    const h = hohmann(sE.a, sD0.a);
    const arrival = planetState(dest, jd + h.days);
    return { h: h, err: wrap180(arrival.lon - (sE.lon + 180)), theta0: sE.lon, arrival: arrival };
  }

  function nextWindow(earth, dest, jd0, tol) { // primera fecha futura donde el error de llegada es un mínimo local <= tol (°)
    const syn = 360 / Math.abs(earth.el[3][1] / 36525 - dest.el[3][1] / 36525);
    const lim = tol === undefined ? 4 : tol;
    let prev = Math.abs(plan(earth, dest, jd0).err), cur = Math.abs(plan(earth, dest, jd0 + 1).err);
    for (let d = 1; d <= syn; d++) {
      const next = Math.abs(plan(earth, dest, jd0 + d + 1).err);
      if (cur <= lim && cur <= prev && cur <= next) return jd0 + d;
      prev = cur; cur = next;
    }
    return jd0;
  }

  SM.physics = { julianDate: julianDate, wrap180: wrap180, solveKepler: solveKepler, planetState: planetState, orbitPoints: orbitPoints, hohmann: hohmann, rocketDv: rocketDv, transferPos: transferPos, plan: plan, nextWindow: nextWindow };
})();
