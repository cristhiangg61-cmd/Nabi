# AUTOPROMPT — Proyecto de aula del Corte 3 "Del dato a la decisión" (Ciencia de Datos, CORHUILA)

## CONTEXTO FIJO
- Estudiante: Cristhian Gaitán Guzmán · modalidad **individual** · Ciencia de Datos (Cód. 69109), Pénsum 40D, Grupo 1,
  Electiva VIII 2026-B · Docente: Jesús Ariel González Bonilla.
- Entrega: **solo Moodle** (actividad `c3-project`), hasta el **sábado 14 de noviembre de 2026, 23:59**. No se usa GitHub.
  Un solo envío con: (1) `FO-IV-159-Apellido1-Apellido2.xlsx`; (2) `Anexos-Apellido1-Apellido2.zip` con las carpetas
  `Anexo 1` (capturas) y `Anexo 2` (cuaderno `.ipynb` ejecutado, datos, documento técnico PDF ≤ 10 páginas, presentación);
  (3) texto en línea con el integrante y el enlace de solo lectura al cuaderno en Colab. **El `.ipynb` va DENTRO del ZIP.**
- Es **precondición** del corte 3: sin entrega, el corte queda en 0,0. Los hitos no tienen nota; la nota es la entrega final.
- Fases con revisión en clase: **0** Definición (sáb 31-oct) · **1** Datos, limpieza y consultas (sáb 7-nov) ·
  **2** Análisis, tablero, historia y sustentación (sáb 14-nov, 4 minutos con el cuaderno en vivo).
- Caso del proyecto (nuevo, desde cero; NO es el caso Siemens ni ningún taller): **Trilladora Cumbres del Macizo S.A.S.**
  (ficticia, Pitalito, Huila). Pregunta: ¿qué proveedores y qué meses (oct-2025 a sep-2026) entregaron café pergamino con peor
  factor de rendimiento? KPI principal: factor de rendimiento ponderado = 70 × Σ kg pergamino ÷ Σ kg excelso (referencia 94).
  Si Cristhian cambia el caso, actualizar esta sección y `PARTES_POR_CAMBIAR.md`.

## REGLAS DURAS DE LA GUÍA (verificar antes de cada entrega)
- Prohibido usar datos de talleres, parcial o ejemplos de clase (planta de empaques, Distribuidora La Ceiba, TecnoAndina).
- Empresa ficticia: tabla principal ≥ 1.000 filas · ≥ 3 clasificaciones (proveedor, municipio, variedad…) · ≥ 12 meses ·
  generación **documentada** (reglas realistas) · ≥ 3 problemas de calidad **a propósito**.
- El cuaderno corre completo con «Reiniciar y ejecutar todo» (si no, tablero y cifras de control valen la mitad).
- IA permitida, pero Cristhian debe poder explicar cada celda en la sustentación: lo que no pueda explicar no suma.
- Dos proyectos con la misma empresa ficticia, mismos datos o mismo cuaderno: 0,0 para ambos → nombre, reglas y semilla propios.

## MODO DE USO
Dame: (a) la fase a ejecutar (0, 1, 2 o FO-IV-159), (b) lo que cambió desde la última vez (empresa, datos, correcciones).
Si faltan datos mínimos, **genéralos y declara el supuesto** en `PARTES_POR_CAMBIAR.md`; solo pregunta lo que no se pueda suponer.

### Fase 0 — Definición (ficha del proyecto)
Ficha de 9 campos en la Parte 1 del cuaderno: integrantes, empresa y tipo, a qué se dedica, problema (qué decisión toma mal hoy),
pregunta (UNA, concreta, medible, con tiempo), KPI principal con fórmula + 2 de apoyo, fuentes y formato, autorización.
- Elegir una idea **fácil de explicar en 4 minutos**, con aplicación práctica y KPI con definición oficial verificable.
- Verificar con búsqueda web cualquier definición del sector (fórmulas, umbrales, normas) y citar la fuente.
- Dejar listo el esqueleto del cuaderno (Partes 0 a 9) para que la Fase 1 solo rellene.

### Fase 1 — Datos, limpieza y consultas (Partes 2 a 5)
1. Generador reproducible (semilla fija, reglas declaradas: temporadas, proveedores buenos y malos) → CSV/Excel con los 3+ problemas.
2. Carga (tamaño y muestra) → diagnóstico con **cifras** (vacíos, duplicados, fechas, textos, imposibles).
3. Limpieza: copia de trabajo, pasos en orden, **antes/después/motivo** de cada corrección, bitácora final.
   Distinguir **imposible** (viola una regla del negocio) de **atípico** (raro pero posible: se investiga, no se borra).
4. Diccionario de datos (tabla, columna, tipo, descripción, ejemplo) y **grano** de la tabla principal.
5. SQLite + ≥ 3 consultas: una `GROUP BY`, una `JOIN`, una que filtre por fechas. Buenas prácticas: solo las columnas necesarias,
   filtrar antes de agrupar, rango de fechas en vez de funciones sobre la columna. Interpretar cada resultado.

### Fase 2 — Análisis, tablero, historia, sustentación y FO-IV-159 (Partes 6 a 9 + formato)
1. KPI por mes, promedio móvil y comparación entre periodos (1.er vs 2.º semestre).
2. Tablero: fila de KPI + ≥ 4 gráficos; **cada título dice el hallazgo**; color con propósito; eje honesto.
3. Cifras de control: filas antes/después, KPI principal y 2 totales que cualquiera pueda recalcular.
4. Historia: contexto → hallazgo → recomendación accionable (qué, quién, cuándo, cómo se mide).
5. Parte 0 «Overview & insights» **en inglés**, ≥ 6 oraciones (problem, data, cleaning, analysis, key insight, recommendation).
6. FO-IV-159 (hojas INFORME, ESTUDIANTE, PRODUCTOS): resumen 150–250 palabras, objetivos con verbo en infinitivo,
   metodología con fases y fechas, ≥ 5 referencias APA/IEEE (incluir Torres, Atehortúa y Caballero, 2018, y la documentación de pandas).
   La hoja ESTUDIANTE lleva la identificación: la completa Cristhian; no inventarla.
7. Guion de sustentación de 4 minutos: pregunta → limpieza más importante → tablero → recomendación; y 3 preguntas probables sobre celdas.

## PRINCIPIOS DE TRABAJO (aprendidos en las Semanas 11 a 15)
- **Una sola fuente de verdad:** las cifras de los textos salen del código, no se escriben a mano; `assert` para lo que afirman los títulos.
- **Reproducible:** semilla fija; ejecutar dos veces y comparar (MD5 de salidas); registrar versiones de Python y librerías.
- **Mirar el resultado:** renderizar y revisar gráficos, PDF y cuaderno ejecutado; los errores de layout no se ven en el código.
- **Tasas con totales**, nunca promedio de tasas (aquí: el factor se pondera por kilos).
- **Medir antes de recomendar** (como con el índice de la Semana 14): no afirmar mejoras sin evidencia.
- **Honestidad:** separar «verificado» de «supuesto»; declarar que los datos son sintéticos; no inventar fuentes, normas ni cifras.
- **Archivo de supuestos:** todo lo inventado o asumido va a `PARTES_POR_CAMBIAR.md` con cómo cambiarlo.
- Entregables en Markdown/PDF/ipynb según lo pedido; presentar los archivos con enlace; no dejar archivos pesados (bases de datos) en la entrega.

## AUTORREVISIÓN FINAL (como evaluador que razona)
- ¿Cada punto de la guía de la fase tiene una sección identificable y completa?
- ¿Los ejemplos y cifras son del caso, no genéricos? ¿Se puede recalcular cada cifra de control?
- ¿El cuaderno corre completo sin errores? ¿Las 3 consultas están interpretadas?
- ¿Cristhian puede explicar cada celda y cada cifra en 4 minutos + 1 pregunta?
- Señalar **1 punto débil real** (no asumir que todo está perfecto).

## RECORDATORIOS
- Hoy es 3-nov-2026: la revisión de la Fase 0 (31-oct) ya pasó; el calendario real es Fase 1 → 7-nov y entrega → 14-nov.
- No sobrecargar con teoría: la rúbrica premia claridad, correspondencia directa con lo pedido y evidencia verificable.
- Confirmar con Cristhian cualquier cambio de caso **antes** de generar datos (un cambio tarde cuesta días).
