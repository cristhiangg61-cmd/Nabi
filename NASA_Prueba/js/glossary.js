// Glosario: sigla, idioma original (en), español (es), origen (o), explicación para niños (k) y técnica (t).
(function () {
  'use strict';
  const SM = (globalThis.SM = globalThis.SM || {});
  SM.glossary = {
    dv: { s: 'Δv', en: 'delta-v', es: 'cambio de velocidad', o: 'Δ (delta, griego) = "cambio"; v = velocidad', k: 'El "empujón" total que el cohete puede dar. Más empujón, más lejos llega.', t: 'Cambio de velocidad que la nave puede lograr con su propelente. Se mide en m/s o km/s.' },
    isp: { s: 'Isp', en: 'Specific Impulse', es: 'Impulso específico', o: 'Inglés', k: 'Qué tan buen "rendidor" es el motor: con más Isp, el mismo combustible empuja más.', t: 'Isp = F / (ṁ·g₀), en segundos. Los motores de hidrógeno rondan 450 s.' },
    ua: { s: 'UA / AU', en: 'Astronomical Unit', es: 'Unidad Astronómica', o: 'UA en español, AU en inglés', k: 'Una regla gigante: 1 UA es la distancia de la Tierra al Sol.', t: '1 UA = 1,496 × 10¹¹ m (≈ 150 millones de km), la distancia media Tierra–Sol.' },
    leo: { s: 'LEO', en: 'Low Earth Orbit', es: 'Órbita Terrestre Baja', o: 'Inglés', k: 'Una "pista de despegue" en el espacio, cerca de la Tierra, donde el cohete da vueltas antes de partir.', t: 'Órbita entre ~200 y 2000 km de altura. Aquí usamos 300 km.' },
    hohmann: { s: 'Hohmann', en: 'Hohmann transfer orbit', es: 'Órbita de transferencia de Hohmann', o: 'Walter Hohmann, ingeniero alemán (1925)', k: 'El camino curvo que gasta menos combustible para ir de un planeta a otro.', t: 'Elipse tangente a la órbita de salida y a la de llegada; la de menor Δv entre dos órbitas circulares coplanares.' },
    tsiolkovsky: { s: 'Tsiolkovsky', en: 'Tsiolkovsky rocket equation', es: 'Ecuación del cohete de Tsiolkovski', o: 'Konstantin Tsiolkovski, ruso (Константин Циолковский, 1903)', k: 'La regla que dice cuánto empuje da un cohete según su combustible.', t: 'Δv = Isp · g₀ · ln(m₀ / m_f).' },
    kepler: { s: 'Kepler', en: "Kepler's equation", es: 'Ecuación de Kepler', o: 'Johannes Kepler, alemán (siglo XVII)', k: 'Con ella sabemos en qué punto de su órbita está cada planeta.', t: 'M = E − e·sen E; relaciona anomalía media (M) y excéntrica (E).' },
    jpl: { s: 'JPL', en: 'Jet Propulsion Laboratory', es: 'Laboratorio de Propulsión a Chorro', o: 'NASA, Pasadena (California)', k: 'El laboratorio de la NASA que mide dónde está cada planeta.', t: 'Fuente de los elementos orbitales usados en data.js.' },
    nasa: { s: 'NASA', en: 'National Aeronautics and Space Administration', es: 'Administración Nacional de Aeronáutica y del Espacio', o: 'Inglés (EE. UU.)', k: 'La agencia espacial de Estados Unidos.', t: 'Organizadora del Space Apps Challenge.' },
    apod: { s: 'APOD', en: 'Astronomy Picture of the Day', es: 'Imagen Astronómica del Día', o: 'Inglés', k: 'Una foto nueva del espacio cada día.', t: 'Servicio de api.nasa.gov.' },
    ventana: { s: 'Ventana de lanzamiento', en: 'Launch window', es: 'Ventana de lanzamiento', o: 'Inglés', k: 'Los planetas se mueven. Hay que salir justo cuando el destino vaya a estar donde llegará el cohete.', t: 'Fecha donde el ángulo de fase Tierra–destino permite la transferencia de Hohmann.' },
    propelente: { s: 'Propelente', en: 'Propellant', es: 'Propelente', o: 'Inglés', k: 'Lo que el cohete quema y expulsa para moverse (combustible + oxidante).', t: 'Masa expulsada; es la diferencia entre m₀ y m_f.' },
    masaseca: { s: 'Masa seca', en: 'Dry mass', es: 'Masa seca', o: 'Inglés', k: 'Lo que pesa el cohete vacío, sin combustible.', t: 'Estructura + motores, sin propelente.' },
    g0: { s: 'g₀', en: 'standard gravity', es: 'gravedad estándar', o: 'Inglés', k: 'Qué tanto te jala la Tierra hacia abajo.', t: 'g₀ = 9,80665 m/s².' },
    gm: { s: 'GM☉', en: 'standard gravitational parameter of the Sun', es: 'parámetro gravitacional del Sol', o: 'G = constante de gravitación (Newton)', k: 'Qué tan fuerte atrae el Sol.', t: 'GM☉ = 1,327 × 10²⁰ m³/s².' },
    si: { s: 'SI', en: 'International System of Units', es: 'Sistema Internacional de Unidades', o: 'Francés: Système International d\'unités', k: 'El idioma común de las medidas: metros, kilogramos, segundos.', t: 'Base de todos los cálculos (m, kg, s). 1 t = 10³ kg.' },
    rtg: { s: 'RTG', en: 'Radioisotope Thermoelectric Generator', es: 'Generador Termoeléctrico de Radioisótopos', o: 'Inglés', k: 'Una "pila nuclear": da energía sin luz del Sol, ideal lejos de casa donde los paneles casi no funcionan.', t: 'Convierte en electricidad el calor de un isótopo radiactivo (p. ej. plutonio-238); potencia casi constante por décadas.' },
    karman: { s: 'Línea de Kármán', en: 'Kármán line', es: 'Línea de Kármán', o: 'Theodore von Kármán, húngaro-estadounidense', k: 'La altura (100 km) donde empieza el espacio.', t: 'Límite convencional de 100 km de altitud entre atmósfera y espacio.' },
    sci: { s: '10ⁿ', en: 'scientific notation', es: 'notación científica', o: 'a × 10ⁿ', k: 'Forma corta de escribir números enormes: 3 × 10⁸ = 300 000 000 (un 3 y ocho ceros).', t: 'a × 10ⁿ con 1 ≤ a < 10; n indica el orden de magnitud.' }
  };
})();
