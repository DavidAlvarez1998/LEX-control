# Proposal — Auditoría de arquitectura (SOLID / clean code) de la API

## Why
Auditoría enfocada en **SOLID + clean architecture** del paquete `@lex/db`
(`lex-control-api/src`), distinta del backlog de deuda técnica de
[[auditoria-malas-practicas-2026-06-17]] (genérico) y de lo ya aplicado por
`api-hardening` / `api-production-grade`. La base arquitectónica es **buena**: módulos
con capas claras (`router → service → repository → dto/schemas`), motor de etapas PURO
(`maquina-etapas.ts`), repositorios con `db: PrismaLike = prisma` **inyectable**. Esto
documenta los puntos donde esa arquitectura se **rompe o se diluye**, priorizado por ROI
real y filtrado de dogmatismo.

> **Correcciones a la auditoría automática (verificadas en código):**
> - **La testabilidad NO está "bloqueada".** Los repositorios ya aceptan `db: PrismaLike`
>   por constructor (`procesos.repository.ts:30-32`) → son mockeables. El gap DIP real es
>   más chico (ver A2/M1), no "no se puede testear nada".
> - **`mapPrismaError` SÍ se usa**: está cableado en el error-handler global
>   (`middleware/error.ts:33`). Los `catch P2002` por-servicio no son un gap de manejo de
>   errores; solo dan mensajes a medida → severidad BAJA, no media.

## Hallazgos (consolidados, deduplicados, con severidad propia)

### 🔴 ALTA

**A1 · Duplicación del motor de reglas API ↔ cliente (DRY / single source of truth).**
`lex-control-api/src/modules/procesos/esquema.ts` y
`lex-control-client/src/lib/procesos.ts` contienen **la misma lógica** duplicada:
`evaluarCondicion`, `puedeSerVerdad`, `campoVisible`, `campoEfectivamenteRequerido`,
`validarDatosContraEsquema`, `documentosRequeridosDeEtapas`. El propio `esquema.ts:3` lo
admite ("esta lógica corre también en el cliente").
*Riesgo:* divergencia silenciosa de reglas `mostrarSi`/`requeridoSi`/plazos → el front
muestra/valida distinto del back (bugs sutiles, justo el tipo de cosa que ya cazamos en el
plazo de subsanación). **Es el hallazgo #1.**
*Fix:* extraer el motor a un módulo compartido consumido por ambos (paquete
`@lex/procesos-core`, o como mínimo un origen único + test de paridad). Evaluar peso del
monorepo vs. paquete liviano.

### 🟠 MEDIA

**M1 · `cartera.service.ts` se saltea la capa repository (capas + DIP + `any`).**
`cartera.service.ts:5` importa `prisma` del `index` y `:19` hace `prisma.ingreso.aggregate`
directo; `:24` define `conSaldo = async (cartera: any)`. Es un service **compartido** por
`contable` y `comercial`, así que el atajo se propaga.
*Fix:* mover la `aggregate` a `ContableRepository`; tipar `cartera` (nada de `any`).

**M2 · Casting `as unknown as EtapaDef[] / CampoEsquema[]` (~13 sitios) sobre el JSON de
Prisma.** `procesos.service.ts` (114, 175, 240, 280, 288, 335, 372…), `procesos.dto.ts`,
`comercial.service.ts:281`. Apaga el tipado justo en el dato más dinámico del sistema.
*Fix:* un helper único `etapasDe(tipo)` / `esquemaDe(tipo)` que castee/valide en **un** lugar
(o `Prisma result extension`). Quita ~13 `as unknown as` y centraliza el punto de fallo.

**M3 · Magic strings de estado** (`"ARCHIVADO"`, `"CERRADO"`, `"EN_PROCESO"`) repetidos en
`procesos.service.ts` (238, 267, 371, 382), `procesos.repository.ts:48`,
`comercial.service.ts` — **aunque el enum `EstadoProceso` ya existe** (`schema.prisma:231`).
*Fix:* usar `EstadoProceso.X`. Barato, elimina el riesgo de typo silencioso.

**M4 · Fallback `DEMO-LEXCONTROL` sin fail-fast en prod (riesgo operacional).**
`config/env.ts:45`: `DOCUMENTOS_RAIZ_PREFIJO ?? "DEMO-LEXCONTROL"`. Si se despliega a prod
sin esa env, **los documentos reales se guardan bajo la raíz DEMO** (colisión/contaminación).
Ya hay patrón fail-fast (`process.exit(1)` :11) e `isProd` (:64) para otras vars.
*Fix:* fail-fast (o warn fuerte) si `isProd` y falta `DOCUMENTOS_RAIZ_PREFIJO`.

**M5 · Lógica de dominio PURA mezclada con orquestación/DB en services (SRP + testabilidad).**
Funciones de negocio enterradas en services, no testeables sin DB:
`recomputarTituloLitigio` (procesos), `totalDesdePlan` (contable, modalidades de cobro),
`calcularComision` (ventas), `espejoColumnasDesdeDatos` (procesos); y funciones largas
(`createProceso` ~65 líneas, `moverEtapa` ~40, `autoavanzarEtapas`).
*Fix de mayor ROI:* separar la **planificación** del autoavance (pura, sobre el motor) de la
**ejecución** (transacción DB) → `planificarAutoavances(proceso, etapas): {etapaKey}[]`
testeable al 100%. Extraer las demás como funciones puras (`construirTituloLitigio`,
`calcularTotalCobro`, `calcularComision`) que el service solo invoca.

### 🟡 BAJA (nice-to-have — mantener pragmatismo)

**B1 · OCP: `if/else` por tipo de campo** (`esquema.ts:181-198`) y `categoriaDoc`
(`procesos.service.ts:499-510`). Tabla data-driven sería más OCP; el de validación de campos
vale si crecen los tipos, `categoriaDoc` es trivial. No urgente.

**B2 · Acoplamiento cruzado de módulos.** `comercial.service.ts:9-12` importa funciones
**internas** de `clientes`, `procesos` y `contable` (`convertirCliente`,
`generarCodigoInterno`, `conSaldo`). *Fix pragmático:* una función de dominio compartida
(p. ej. `convertirProspectoAClienteYProceso`) en un módulo común — **no** un service-interface
con DI container.

**B3 · Helpers de fecha duplicados** (`startOfDay`/`endOfDay`/`DIA_MS` en
`comercial.service.ts` y `ventas.service.ts`) → `shared/dateUtils.ts`.

**B4 · `catch P2002` repetido (~16).** No es gap (mapPrismaError ya está global); opcional un
helper `conflicto(entidad)` para los mensajes a medida.

## Non-goals (lo que NO recomiendo — sería over-engineering acá)
- **DI container / inyectar todo por constructor** en 15 services. La inyección que ya
  existe (repos con `PrismaLike`) alcanza para tests; el resto es ceremonia.
- **Convertir cada `if/else` en registry de estrategias** por dogma OCP.
- **Segregar `TenantContext`** en 3 interfaces (ISP) — molesto, no aporta hoy.
- **Monorepo completo** solo por el core de procesos: evaluar, pero el mínimo viable es un
  paquete/módulo compartido para A1.

## Priorización sugerida
1. **A1** (divergencia de reglas = bugs reales) — el de mayor valor.
2. **M1, M3, M4** (atajos de capa, enum, riesgo prod) — baratos y de bajo riesgo.
3. **M2, M5** (casting centralizado, extraer funciones puras) — mejoran tipado y testabilidad.
4. **B1–B4** — backlog, oportunista.

## Solución validada (la "manera correcta", contra restricciones reales)

> Validado contra el código y `CLAUDE.md`. **NO implementado** — esto es el plan.

**A1 (duplicación motor) — restricción dura:** no hay monorepo/workspace tooling y los
frontends **no dependen de `@lex/db`** (CLAUDE.md). Un paquete compartido `@lex/procesos-core`
exigiría tooling de publish/link que hoy no existe → es la opción "correcta" de libro pero de
mayor costo. **Manera correcta pragmática y por fases:**
1. **Ya (tripwire):** test de **paridad** con casos golden (mismos inputs → mismo output) que
   corra las funciones de `api/esquema.ts` y `client/lib/procesos.ts` y falle si divergen. Cero
   tooling nuevo, ataca el riesgo real (divergencia silenciosa) hoy.
2. **Después (si crece):** extraer a un paquete liviano consumido por ambos (file:/git dep) o
   evaluar monorepo. No antes de que el tripwire demuestre que duele.

**M1 (cartera prisma directo):** mover el `aggregate` a `ContableRepository.valorPagado(...)`;
tipar `cartera` (sin `any`). El patrón repository ya existe → cambio mecánico, cero riesgo.

**M2 (casting JSON):** helper único `etapasDe(tipo)` / `esquemaDe(tipo)` que castee/valide en un
solo lugar; reemplazar los ~13 `as unknown as`. Centraliza el punto de fallo.

**M3 (magic strings):** usar el enum **`EstadoProceso`** (ya existe en `schema.prisma:231`) en
vez de `"ARCHIVADO"/"CERRADO"/"EN_PROCESO"`. Trivial.

**M4 (config DEMO):** `config/env.ts` ya tiene `isProd` y patrón `process.exit(1)` → agregar
fail-fast si `isProd` y falta `DOCUMENTOS_RAIZ_PREFIJO`. Trivial, cierra riesgo operacional.

**M5 (lógica pura en services):** el motor (`maquina-etapas.ts`) ya es PURO → extraer
`planificarAutoavances(proceso, etapas)` (pura, testeable) separando la planificación de la
ejecución (tx); y `construirTituloLitigio` / `calcularTotalCobro` / `calcularComision` como
funciones puras que el service invoca. Sube cobertura sin DB.

> **NO hacer** (validado como over-engineering para este equipo): DI container, inyectar todo
> por constructor (los repos ya aceptan `db: PrismaLike`), segregar `TenantContext`, registries
> por dogma OCP. Esas las dejo explícitamente fuera del plan.

## Rollback
Cada punto es independiente y de bajo riesgo (extracciones puras, constantes, un fail-fast de
config, un test de paridad). Revertir por commit.
