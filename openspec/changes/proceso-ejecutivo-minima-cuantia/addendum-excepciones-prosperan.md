# Addendum — Terminación cuando las excepciones PROSPERAN (a favor del demandado)

> Estado: **PLAN → IMPLEMENTAR**. Hermano del addendum `addendum-rechazo-subsanacion.md`
> (mismo patrón: etapa terminal por condición, sin tocar el motor).

## El hueco
Tras la notificación del mandamiento, si el demandado **contesta** (`contesto = "Sí"`)
hay **audiencia** y el juez dicta **sentencia sobre las excepciones**
(`sentenciaExcepciones`: `"Prosperan"` / `"No prosperan"`).

- `"No prosperan"` → sigue la ejecución → **Impulsos** → liquidación → avalúo y remate.
- `"Prosperan"` → **el proceso TERMINA a favor del demandado**: NO sigue la ejecución
  (no hay liquidación, avalúo ni remate).

Hoy ese segundo caso **no tiene cierre**: no existe etapa terminal para "excepciones
probadas". El proceso quedaría colgado o pasaría indebidamente por "Impulsos". (Es el
mismo tipo de hueco que tenía el rechazo de la subsanación.)

## La realidad legal
Si el juez declara **probadas las excepciones** del ejecutado, la sentencia es a su
favor: se **niega el seguir adelante con la ejecución**, se levantan las medidas
cautelares y el proceso termina. **No hay remate.** En mínima cuantía (única instancia)
contra esa sentencia solo procede **reposición** (no apelación) — no se modela como rama.

## La solución (fiel al patrón de `archivado_rechazo`)
1. **Nueva etapa terminal** `terminado_excepciones` (orden 11, hermana de `terminacion`
   y `archivado_rechazo`), que se activa cuando `sentenciaExcepciones = "Prosperan"`:

   ```jsonc
   {
     "key": "terminado_excepciones",
     "nombre": "Terminación por excepciones probadas (a favor del demandado)",
     "orden": 11,
     "terminal": true,
     "resultado": "El juez declaró probadas las excepciones del demandado: el proceso termina a su favor; no sigue la ejecución (sin liquidación, avalúo ni remate). En mínima cuantía solo procede reposición.",
     "disponibleSi": { "campo": "sentenciaExcepciones", "igualA": "Prosperan" }
   }
   ```

2. **Gatear la etapa `impulsos`** con la condición "la ejecución sigue" (igual que el
   `mostrarSi` de sus campos), para que **NO** se transite cuando las excepciones prosperan:

   ```jsonc
   "disponibleSi": { "alguna": [
     { "campo": "contesto", "igualA": "No" },
     { "todas": [ { "campo": "contesto", "igualA": "Sí" }, { "campo": "sentenciaExcepciones", "igualA": "No prosperan" } ] }
   ] }
   ```

## Por qué NO toca el motor
`terminalDecidido` (maquina-etapas.ts) salta a la **única** etapa terminal con
`disponibleSi` cumplido. Con `sentenciaExcepciones = "Prosperan"`:
- `archivado_rechazo` (inadmite+rechazar) → no se cumple.
- `terminado_excepciones` (Prosperan) → se cumple → único candidato → salta ahí.

El service ya hace `siguienteEtapaAuto(...) ?? terminalDecidido(...)`, así que basta el
seed. La terminal queda en **estado `CERRADO`** (como `archivado_rechazo` / verbal),
sin cambio transversal del motor.

## Verificación
- Simulación del motor: con `contesto=Sí` + `sentenciaExcepciones=Prosperan` → aterriza
  en `terminado_excepciones`; con `No prosperan` → sigue a `impulsos`; con `contesto=No`
  → `impulsos`. (test en `tests/`).
- `pnpm seed:catalogo` aplicado; `pnpm test` + builds verdes.
