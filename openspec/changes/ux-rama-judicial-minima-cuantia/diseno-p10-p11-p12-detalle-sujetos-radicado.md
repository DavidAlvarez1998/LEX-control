# P11/P10/P12 a fondo — Detalle, Sujetos→Partes y preview del radicado

Profundización del cluster "consumir más de la API + UX del radicado". Diseño listo-para-implementar.
Sigue siendo **plan** (no se implementa aquí). Reusa los patrones del módulo `rama-judicial`.

---

## P11 — Card "Estado en el juzgado" (Endpoint Detalle)

### Capacidad (verificada)
`GET /Proceso/Detalle/{idProceso}` → `{ tipoProceso, claseProceso, subclaseProceso, ponente, recurso,
ubicacion ("Secretaria"), contenidoRadicacion, codDespachoCompleto, fechaProceso, ultimaActualizacion }`.
El dato estrella es **`ubicacion`**: dónde está físicamente el expediente (Secretaría, Despacho, Archivo…).

### Backend
- Cliente: `obtenerDetalle(idProceso): Promise<DetalleRama>` (DTO normalizado).
- Cuándo se trae: **cachear en el sync** (barato, 1 request más por proceso) → guardar en
  `datos._meta.rama` o columnas. Mínimo viable: endpoint on-demand `GET /procesos/:id/rama/detalle`.
- Si se cachea, exponerlo en `getDetalle` del proceso para pintarlo sin nueva llamada.

### UI (ficha) — bloque compacto dentro del panel del juzgado
```
 🏛️ Estado en el juzgado                         (sincronizado hace 2 h)
 Ubicación: Secretaría        ·  Tipo/Clase: Ejecutivo · Mínima cuantía
 Despacho: 002 Civil Municipal de Pereira  ·  Últ. actualización Rama: 17-jun
```
- "Ubicación" con realce (es lo más accionable: saber dónde está el expediente).
- `contenidoRadicacion` (texto largo: "83 folios, 1 CD…") como tooltip/expandible, no en primer plano.

### Casos borde / esfuerzo
- Reservado/no publicado → ocultar el bloque o "sin datos del juzgado".
- Esfuerzo **medio**: 1 método de cliente + DTO + (cachear o endpoint) + bloque de UI.

---

## P10 — Importar Partes desde Sujetos

### Capacidad (verificada)
`GET /Proceso/Sujetos/{idProceso}` → `[{ idRegSujeto, tipoSujeto ("Demandante"/"Demandado"/...),
nombreRazonSocial, identificacion, esEmplazado }]`. Mejor que el string concatenado `sujetosProcesales`.

### Backend
- Cliente: `obtenerSujetos(idProceso): Promise<SujetoRama[]>` (DTO).
- Servicio `sugerirPartesRama(t, procesoId)`: trae sujetos, los **cruza con las `ParteProceso` actuales**
  (por nombre normalizado / identificación) → marca cuáles ya están y cuáles faltan.
- `importarPartesRama(t, procesoId, { sujetos })`: crea `Litigante` + `ParteProceso` para los faltantes.
  - **Mapeo `tipoSujeto` → `RolParte`:** Demandante→DEMANDANTE/EJECUTANTE (según el tipo), Demandado→
    DEMANDADO/EJECUTADO. Tabla de equivalencias por jurisdicción/tipo.
  - **No pisa** lo existente: solo agrega los que faltan (el abogado confirma).
  - ⚠️ **Coordinar con la sesión paralela** que agregó `naturalezaJuridica` a Litigante/ParteProceso:
    al crear el Litigante desde un Sujeto, inferir `tipoPersona` (¿NIT/razón social→JURÍDICA?) y dejar
    naturaleza/documento como "por completar" si la Rama no lo da con certeza.
- Endpoints: `GET /procesos/:id/rama/sujetos` · `POST /procesos/:id/rama/partes/importar`.

### UI (ficha / al vincular radicado)
```
 La Rama reporta estas partes:
   Demandante  FINOVA SAS                  → ya está (nuestro cliente) ✓
   Demandado   ELDER JOVANNY GESAMA NOGUERA   [ crear como Ejecutado ]
                              [ Importar las que faltan ]
```
- Cada parte faltante: botón para crearla con el rol sugerido (editable).
- Aviso si la Rama trae menos/más partes que las nuestras (cotejo).

### Casos borde / esfuerzo
- Identificación suele venir `null` en la Rama → crear Litigante con documento "por completar".
- Nombres con formato distinto ("Y OTRO.") → no autocrear ciegamente; mostrar para que el abogado decida.
- Esfuerzo **medio** (mapeo de roles + dedup + UI de cotejo).

---

## P12 — Validación en vivo + preview del radicado antes de vincular

### Objetivo
Que al pegar el radicado el abogado VEA qué proceso es **antes** de vincularlo, y que el autollenado
sea **explícito** (confirma), no "mágico". Resuelve gaps D/I.

### Flujo
1. Usuario teclea el radicado. Contador de dígitos en vivo (ya existe).
2. Al llegar a **23 dígitos** (debounce ~400 ms) → `GET /procesos/validar-radicado?radicado=…`
   (**endpoint ya existe**; sin cambios de backend).
3. Tarjeta de **preview** (sin guardar nada):
```
 Radicado [ 66001400300220260070400 ]   ✓ 23 dígitos
 ┌ Encontrado en la Rama ───────────────────────────────────┐
 │ JUZGADO 002 CIVIL MUNICIPAL DE PEREIRA · radicó 04-jun-26   │
 │ Demandante: FINOVA SAS · Demandado: ELDER J. GESAMA …       │
 │                 [ Vincular y traer datos ]                  │
 └─────────────────────────────────────────────────────────────┘
```
4. "Vincular y traer datos" → guarda radicado + dispara el sync (lo que hoy hace al Guardar). El
   juzgado/fecha/actuaciones se llenan tras confirmar.

### Estados
- `encontrado` → preview + botón. · `procesos:[]` → "No aparece aún en la Rama (puede tardar días);
  puedes vincularlo igual." · `esPrivado` → "Reservado: no veremos sus actuaciones." · error/red →
  "No se pudo consultar; reintenta." · `<23 díg` → solo el contador, **no** llama.

### Dónde aplica
- **Ficha** (RadicadoDato) y **form de crear** (mismo componente de input de radicado).

### Esfuerzo
**Medio**, 100% front (debounce + tarjeta de preview + estados). Backend ya está. Bajo riesgo.

---

## Resumen de cambios de datos de este cluster
| Propuesta | Cambio de datos |
|---|---|
| P11 Detalle | ninguno obligatorio (on-demand) · opcional cachear en `datos._meta.rama` |
| P10 Sujetos | ninguno (crea Litigante/ParteProceso existentes) · coordinar con `naturalezaJuridica` |
| P12 preview | ninguno (usa endpoint existente) |

Cluster de bajo cambio de modelo: mucho valor de UX por cliente nuevo + UI. P12 es el más barato
(solo front) y de los más visibles.
