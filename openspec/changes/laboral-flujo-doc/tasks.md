# Tasks — laboral-flujo-doc

## 0. Validación del diseño
- [x] Confirmado con el usuario: demanda = adjuntar PDF (sin pretensiones/hechos)
- [x] Confirmado: extender el motor (condiciones compuestas) e implementar ya
- [x] No basarse en la tutela actual (está en ajuste paralelo) — el diseño se funda solo en el doc

## 1. Motor: condiciones compuestas (AND/OR)
- [x] API `esquema.ts`: `Condicion` += `{todas}`/`{alguna}` + `evaluarCondicion` recursivo
- [x] API `esquema.ts`: `camposDeCondicion`, `puedeSerVerdad`, `condicionPendiente` (auto-avance no se cuelga en demandado+única)
- [x] API `procesos.router.ts`: auto-avance usa `condicionPendiente`
- [x] API `catalog.schemas.ts`: `condicionSchema` recursivo (z.lazy) + refs de campo vía `camposDeCondicion`
- [x] Cliente `lib/procesos.ts`: `Condicion` compuesta + `evaluarCondicion` + `camposDeCondicion`
- [x] Cliente `procesos/[id]/page.tsx`: mensaje de "etapa no disponible" guía al primer campo pendiente también en compuestas
- [x] Tests motor: AND/OR/anidado + puedeSerVerdad + condicionPendiente (20 tests esquema, 413 total)

## 2. Seed: reescribir "Proceso Laboral" (prisma/seed-tipos.json)
- [x] `esquemaFormulario` nuevo (sin pretensiones/hechos; 30 campos, 4 al crear)
- [x] `etapas` (15): presentacion→admision→[subsanacion|recurso_rechazo]→retiro→[archivado|traslado]→contestacion→preparacionAudiencia→citacionAudiencia→[audienciaUnica|art77→art80]→recurso→terminada
- [x] disponibleSi compuestos (admision OR; subsanación/recurso = todas[admision, decisionAuto]; audiencias/contestación por instancia)
- [x] plazos: contestación 10 háb., subsanación 5 háb., recurso 3 cal.
- [x] `pnpm seed:catalogo` (38 tipos actualizados, esquemaVersion++)
- [x] Simulación de los 4 flujos (Python) → todos caminan y terminan; demandado/única salta admisión sin colgarse

## 3. Cliente: form de creación en orden del doc (solo LABORAL)
- [x] `etapasDeCreacion(etapas)` (nivel de entrada) — los docs de creación son los de la etapa de entrada, no de todo el flujo (fix del bug que pedía auto-admision.pdf/sentencia.pdf al crear)
- [x] `nuevo/page.tsx`: docsFaltan + docsASubir + slot requierePoder + fallback usan `etapasDeCreacion`
- [x] Card "Radicación" (# radicado + juzgado) tras "Datos del proceso" para LABORAL; bloque genérico "Datos judiciales" excluye laboral

## 4. Verificación
- [x] `pnpm build` API (tsc) + cliente verdes
- [x] 413 tests API verdes
- [x] Simulación de motor de los 4 flujos OK
- [ ] Smoke manual UI: crear los 4 flujos en el navegador, ver orden del form + stepper + plazos + subir documentos

## 5. OpenSpec / cierre
- [ ] Archivar tras smoke manual (fusionar deltas a specs canónicas)
- [ ] Commit (api + client + superrepo) — SIN pushear
