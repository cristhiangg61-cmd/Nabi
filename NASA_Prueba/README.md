# CodecNasaProyectGame — Misión Orbital

Juego educativo basado en la física real de las órbitas, para el NASA Space Apps Challenge 2026 (equipo codec37).
Elige un planeta, una fecha de lanzamiento y el tamaño de tu cohete, y mira cómo recorre la órbita de transferencia en un mapa 2D del sistema solar.

## Cómo ejecutarlo
Abre la carpeta en VS Code, clic derecho en `index.html` → **Open with Live Server**. No necesita instalar nada más.

## Modos
- **Explorador** (por defecto, para niños): tanque con deslizador, pistas y cálculo en frases.
- **Ingeniero**: Isp, masas, Δv y cálculo paso a paso con notación científica.
- Los botones «?» y «Glosario» explican cada sigla (idioma original, español, versión fácil y técnica).

## Estructura
- `js/data.js`: elementos keplerianos de los planetas (JPL) y constantes físicas.
- `js/physics.js`: Kepler, Hohmann y Tsiolkovsky (sin DOM, se prueba con Node).
- `js/map.js` y `js/main.js`: mapa en canvas, interfaz y animación.
- `js/learn.js` y `js/glossary.js`: modo Explorador/Ingeniero, pistas, cálculo paso a paso y glosario.
- `js/api.js` y `js/config.js`: API de NASA (APOD) y clave. Son públicas al publicar: solo claves gratuitas, nunca privadas.
- `test/physics.test.js`: `node test/physics.test.js`.

## Simplificaciones (decirlas en la demo)
Órbitas coplanares, transferencia de Hohmann, sobrevuelo sin captura orbital, ascenso a órbita baja fijo en 9,4 km/s y tolerancia de llegada de 4°.

## Datos y créditos
- Posiciones de los planetas: JPL Solar System Dynamics, «Approximate Positions of the Planets» (Tabla 1, 1800–2050).
- Foto del día: NASA APOD API (api.nasa.gov).
- Parte del código se desarrolló con asistencia de IA (Claude, Anthropic). Ajusten esta línea según lo que pida el formulario de Space Apps.

## Flujo de trabajo en equipo
1. Cada persona trabaja en su rama: `git switch -c mi-cambio`.
2. `git add -A`, `git commit -m "qué cambié"`, `git push -u origin mi-cambio`, y abrir un Pull Request.
3. Publicación: Settings → Pages → Deploy from a branch → rama y carpeta `/ (root)`. Ese enlace público va en el formulario.

## Flujo del juego
1. **Diseña tu misión** (`js/mission.js`): objetivo, lanzador, energía, comunicaciones e instrumentos, con límites de masa y presupuesto.
2. **Ascenso** (`js/ascent.js`): minijuego para llegar a 100 km; el empuje depende del lanzador.
3. **Viaje por las órbitas** (`js/main.js`, `js/map.js`): transferencia de Hohmann sobre el mapa 2D.
4. **Operación y reporte**: tres turnos con eventos aleatorios y puntuación explicada.
Pendiente: más objetivos (Luna, asteroide) y más eventos.
