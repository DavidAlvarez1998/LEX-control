# spec — API Rama Judicial (CPNU): contrato de consulta de actuaciones

Contrato de la **Consulta de Procesos Nacional Unificada** (API pública oficial de la Rama
Judicial de Colombia). Documenta **qué pide y qué retorna**. Validado en vivo (SERVICIUDAD).

## Base y reglas de acceso

- **Base URL:** `https://consultaprocesos.ramajudicial.gov.co:448/api/v2`
- **Puerto `448`** (¡no 443!). HTTPS.
- **Sin API key** — es pública.
- **Headers OBLIGATORIOS** (si faltan → `403`):
  - `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36` (User-Agent de
    navegador; un cliente "vacío" tipo curl/axios por defecto es bloqueado).
  - `Accept: application/json`
- **Rate-limiting agresivo:** golpear rápido → `403`/`429`. Exige espaciar requests (ver §4).
- **Latencia observada:** ~0.4 s por request, conexión estable.

> **Validación en vivo desde lex-control-api (2026-06-22):** egress a `:448` OK. A → `200` 0.38 s,
> `idProceso 1810780324`. B → `200` 0.50 s, 40 actuaciones/pág, 64 total, 2 páginas, primera
> "RECIBE MEMORIALES ONLINE" (2026-03-09). **Matiz:** una petición SIN User-Agent de navegador (curl
> con su UA por defecto) **devolvió 200, no 403** → el 403 del doc parece ligado al rate-limiting/tipo
> de cliente, no a la ausencia estricta de UA de navegador. Aun así, **enviar siempre el UA de
> navegador** por seguridad (el doc lo exige y el comportamiento puede variar bajo carga).

## Endpoint A — Radicado → idProceso

```
GET /Procesos/Consulta/NumeroRadicacion?numero={radicado}&SoloActivos=false&pagina=1
```

- `numero` = **radicado de 23 dígitos**.
- `SoloActivos=false` para no filtrar por estado.

**200 — encontrado:**
```json
{
  "tipoConsulta": "NumeroRadicacion",
  "procesos": [{
    "idProceso": 1810780324,
    "llaveProceso": "66001333300320140049500",
    "fechaProceso": "2014-06-06T00:00:00",
    "fechaUltimaActuacion": "2026-03-09T00:00:00",
    "despacho": "JUZGADO 003 ADMINISTRATIVO DE PEREIRA",
    "departamento": "RISARALDA",
    "sujetosProcesales": "Demandante: -SERVICIUDAD ESP- | Demandado: ...",
    "esPrivado": false
  }],
  "paginacion": { "cantidadRegistros": 1, "cantidadPaginas": 1, "pagina": 1 }
}
```

- **Lo que se usa:** `procesos[0].idProceso`.
- **`procesos: []` ⇒ el radicado NO existe en la Rama Judicial.** Es un `200`, **no un error**:
  hay que tratarlo como "sin proceso", no como fallo.
- Campos útiles para enriquecer/validar nuestro registro: `fechaUltimaActuacion` (para saber si hay
  novedad sin descargar todo), `despacho`, `sujetosProcesales`, `esPrivado`.

## Endpoint B — idProceso → Actuaciones (paginado)

```
GET /Proceso/Actuaciones/{idProceso}?pagina=1
```

**200:**
```json
{
  "actuaciones": [{
    "fechaActuacion": "2026-03-09T00:00:00",
    "actuacion": "RECIBE MEMORIALES ONLINE",
    "anotacion": "El Señor(a): FREDY AUGUSTO OSPINA ...",
    "fechaInicial": null,
    "fechaFinal": null,
    "fechaRegistro": "..."
  }],
  "paginacion": { "cantidadRegistros": 64, "cantidadPaginas": 2, "pagina": 1, "registrosPagina": 40 }
}
```

- **40 actuaciones por página.** Para traerlas todas hay que recorrer `paginacion.cantidadPaginas`
  (pedir `?pagina=2..N`), respetando un delay entre páginas (anti rate-limit).
- Campos por actuación: `fechaActuacion`, `actuacion` (título del movimiento), `anotacion`
  (detalle), `fechaInicial`, `fechaFinal`, `fechaRegistro`.

## Flujo completo (validado)

```
radicado (23 díg.) ──A──▶ idProceso ──B(paginado)──▶ [actuaciones]
```

Pseudocódigo de referencia (del módulo fuente, autocontenido con axios):
```ts
async function consultarProceso(radicado) {
  const idProceso = await obtenerIdProceso(radicado);        // A; null si procesos:[]
  if (!idProceso) return { encontrado: false, actuaciones: [] };
  const actuaciones = await obtenerActuaciones(idProceso);   // B; recorre todas las páginas
  return { encontrado: true, idProceso, total: actuaciones.length, actuaciones };
}
```

## Pruebas reales (del doc fuente)

| Caso | Entrada | Resultado |
|---|---|---|
| Radicado inexistente | `66001333100020180001400` | `200` → `procesos: []` (no existe) |
| Radicado válido | `66001333300320140049500` | `200` → `idProceso: 1810780324` |
| Actuaciones | `idProceso 1810780324` | `200` → 64 actuaciones / 2 páginas, última `2026-03-09` |

## §4 — Estrategia anti-bloqueo (rate limiting + retry)

Config usada en producción (SERVICIUDAD, `rateLimiting.config.ts`):
```
batchSize: 8                  // procesa de a 8 radicados
delayBetweenBatches: 5000 ms  // 5 s entre lotes
delayBetweenRequests: 1200 ms // 1.2 s entre requests
delayBetweenPages: 800 ms     // 0.8 s entre páginas de actuaciones
maxConsecutiveErrors: 3
pauseOnMaxErrors: 45000 ms     // pausa 45 s tras 3 errores seguidos
requestTimeout: 20000 ms
retry: { attempts: 4, initialDelay: 3000, maxDelay: 20000, exponentialBackoff: true }
```
- Reintenta con **backoff exponencial** ante `403, 429, 500, 502, 503, 504`.

## Variables de entorno (del doc fuente)

```
RAMA_JUDICIAL_URL=https://consultaprocesos.ramajudicial.gov.co:448/api/v2
ACTUALIZAR_PROCESOS_CRON=0 0 * * *   # cron diario 00:00
```

## Prueba rápida (cURL)

```bash
# A) radicado → idProceso
curl "https://consultaprocesos.ramajudicial.gov.co:448/api/v2/Procesos/Consulta/NumeroRadicacion?numero=66001333300320140049500&SoloActivos=false&pagina=1" \
  -H "User-Agent: Mozilla/5.0"
# B) idProceso → actuaciones
curl "https://consultaprocesos.ramajudicial.gov.co:448/api/v2/Proceso/Actuaciones/1810780324?pagina=1" \
  -H "User-Agent: Mozilla/5.0"
```

## Superficie COMPLETA de la API (explorada en vivo 2026-06-22 — NO consumida aún)

Sondeo en vivo con `idProceso 1810780324`. La CPNU expone bastante más que radicado→
idProceso→actuaciones. Documentado para futuras fases; **hoy solo se consumen A y B**.

### Campos crudos del Endpoint A (Consulta) — además de los ya usados
`idConexion`, `llaveProceso` (= el radicado), `cantFilas`. (Ya se usan `idProceso`,
`despacho`, `fechaProceso`, `fechaUltimaActuacion`, `departamento`, `sujetosProcesales`, `esPrivado`.)

### Endpoint C — Detalle del proceso  `GET /Proceso/Detalle/{idProceso}`  → 200
Devuelve un objeto con: `tipoProceso` (p. ej. "ORDINARIO"), `claseProceso` ("REPETICION"),
`subclaseProceso`, `ponente`, `recurso`, `ubicacion` ("Secretaria"), `contenidoRadicacion`
(texto libre: "TRAE UN ORIGINAL EN 83 FOLIOS 1CD…"), `codDespachoCompleto`,
`fechaProceso`, `ultimaActualizacion`, `idRegProceso`.
→ **Uso potencial:** autollenar tipo/clase/ubicación del proceso.

### Endpoint D — Sujetos (partes ESTRUCTURADAS)  `GET /Proceso/Sujetos/{idProceso}`  → 200
`{ sujetos: [{ idRegSujeto, tipoSujeto: "Demandante"|"Demandado", nombreRazonSocial,
identificacion, esEmplazado, cant }], paginacion }`.
→ **Uso potencial:** autopoblar el panel "Partes" (mejor que el string `sujetosProcesales`).

### Endpoint E — Documentos del expediente  `GET /Proceso/Documentos/{idProceso}`  → 200
Array de `{ idRegDocumento, idConexion, consActuacion, nombre, descripcion, tipo, fechaCarga }`
(en el caso de prueba, 7 documentos).
> **GOTCHA:** cuando un proceso VÁLIDO aún **no tiene documentos publicados**, este
> endpoint devuelve **404** (no una lista vacía). El client lo trata como "sin
> documentos" (lista vacía, `getJson(..., { on404Null: true })`), NO como error —
> así la ficha muestra "El expediente no tiene documentos publicados" en vez de
> "No se pudieron consultar los documentos". Verificado en vivo (idProceso 3281956241:
> actuaciones OK, documentos 404).

### Endpoint F — DESCARGA del documento  `GET /Descarga/Documento/{idRegDocumento}`  → 200
Devuelve el **PDF real** (`application/pdf`; verificado: 384 KB, 2 páginas, cabecera `%PDF-`).
→ **Uso potencial (alto valor):** importar los documentos del juzgado al proceso (tecnovapp),
documento por documento (cada uno = 1 request → respetar el §4 anti-bloqueo).

### Campos crudos del Endpoint B (Actuaciones) — además de los ya usados
`idRegActuacion`, `consActuacion` (consecutivo), `llaveProceso`, `codRegla`, y
**`conDocumentos`** (bool: la actuación tiene documentos anexos — en el caso de prueba,
21 de 40 en la pág. 1). → enlaza actuación ↔ documentos descargables (E/F).

> **Notas:** todo lo anterior comparte el rate-limiting (§4) — importar el expediente
> completo son N requests, hay que espaciarlas. La descarga es **por documento**
> (`idRegDocumento`); no hay "descargar todo de una".
