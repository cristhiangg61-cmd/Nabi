// Llamadas a APIs de NASA. Todo con try/catch: si falla, el juego sigue funcionando con data.js.
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});

  async function apod() { // Astronomy Picture of the Day (api.nasa.gov)
    const key = (SM.config && SM.config.NASA_API_KEY) || 'DEMO_KEY';
    const r = await fetch('https://api.nasa.gov/planetary/apod?api_key=' + encodeURIComponent(key));
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }

  // Experimental: vector de estado heliocéntrico desde JPL Horizons. Puede fallar por CORS; devuelve null si falla.
  async function horizonsVector(commandId, isoDate) {
    const end = new Date(Date.parse(isoDate + 'T00:00:00Z') + 86400000).toISOString().slice(0, 10);
    const q = new URLSearchParams({ format: 'json', COMMAND: "'" + commandId + "'", EPHEM_TYPE: 'VECTORS', CENTER: "'500@10'", START_TIME: "'" + isoDate + "'", STOP_TIME: "'" + end + "'", STEP_SIZE: "'1d'", OUT_UNITS: 'AU-D' });
    try {
      const r = await fetch('https://ssd.jpl.nasa.gov/api/horizons.api?' + q);
      if (!r.ok) return null;
      const j = await r.json();
      return j.result || null;
    } catch (e) { return null; }
  }

  SM.api = { apod: apod, horizonsVector: horizonsVector };
})();
