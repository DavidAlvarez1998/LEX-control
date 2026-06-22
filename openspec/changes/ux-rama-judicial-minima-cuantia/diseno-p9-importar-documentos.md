# P9 a fondo — Importar los documentos del expediente (PDF de la Rama)

Profundización lista-para-implementar de la propuesta de **mayor impacto**: traer los documentos que
el juzgado publica (PDFs) y guardarlos en el proceso. Sigue siendo **diseño** (no se implementa aquí).
Depende de la sesión paralela del *uploader de documentos* — coordinar antes de codificar.

## 1. Capacidad de la Rama (verificada en vivo)
- `GET /Proceso/Documentos/{idProceso}` → `[{ idRegDocumento, idConexion, consActuacion, nombre,
  descripcion, tipo, fechaCarga }]` (en el caso de prueba, 7 documentos).
- `GET /Descarga/Documento/{idRegDocumento}` → **PDF** (`application/pdf`; verificado: 200, 384 KB, `%PDF-`).
- Actuaciones traen `conDocumentos: boolean` y `idRegActuacion` (para correlacionar actuación↔documentos).
- `consActuacion` en el documento permite ligar cada documento a su actuación.

## 2. Cómo se guardan documentos HOY (a reusar tal cual)
Verificado en `procesos.service.ts` + `documentos/documentos.client.ts`:
1. `subirDocumento({ archivo: Buffer, nombreArchivo, documento: proceso.codigoInterno,
   carpeta: carpetaModulo(proceso.empresa, "PROCESOS"), tipo: mimetype })` → `{ path }` (tecnovapp).
2. `createDocumento({ procesoId, nombre, url: path, tipo, subidoPorId, categoria: categoriaDoc(nombre) })`.
3. `construirUrlDocumento(path)` reconstruye la URL pública. `categoriaDoc(nombre)` infiere la categoría
   (AUTO/SENTENCIA/…) por palabras del nombre.
→ **Importar un PDF de la Rama = exactamente este flujo**, con el Buffer que baja `descargarDocumento`.

## 3. Modelo de datos (1 cambio aditivo)
- `DocumentoProceso.origenRamaIdReg String?` + índice `@@unique([procesoId, origenRamaIdReg])`.
  - Idempotencia: re-importar NO duplica (si ya existe ese `idRegDocumento` en el proceso, se omite).
  - Permite marcar en la UI "ya está en el proceso ✓".
- Opcional: `DocumentoProceso.origenRamaActuacion Int?` (= `consActuacion`) para agrupar por actuación.
- `pnpm push` (aditivo, nullable). Sin pérdida.

## 4. Backend

### 4.1 Cliente rama-judicial (extender el módulo, mismos patrones)
- `obtenerDocumentos(idProceso): Promise<DocumentoRama[]>` (Endpoint Documentos → DTO normalizado:
  `{ idRegDocumento, descripcion, fechaCarga, consActuacion }`).
- `descargarDocumento(idRegDocumento): Promise<{ buffer: Buffer; tipo: string } | null>` (Endpoint
  Descarga). Valida `content-type` empieza por `application/pdf`; aplica límite de tamaño (p. ej.
  `RAMA_JUDICIAL_DOC_MAX_MB`, default 25) y timeout; usa el mismo `getJson`/transporte pero recibiendo
  binario (variante `getBuffer`). Devuelve null si el tipo/size no califica (se omite, no rompe el lote).

### 4.2 Servicio (on-demand, NUNCA en el sync automático)
- `listarDocumentosRama(t, procesoId)`: usa `idProcesoRama` (o lo resuelve), llama `obtenerDocumentos`,
  y **cruza con lo ya importado** (`origenRamaIdReg`) → devuelve `[{ idRegDocumento, descripcion,
  fechaCarga, yaImportado: boolean }]`. Solo lectura (no descarga binarios).
- `importarDocumentosRama(t, procesoId, { idRegs?: string[] })`: para cada idReg seleccionado (o todos
  los no importados): `descargarDocumento` → `subirDocumento` → `createDocumento` (con `origenRamaIdReg`).
  - **Idempotente** (salta los ya importados por el `@@unique`).
  - **Anti-bloqueo**: secuencial con `delayRequestMs` entre descargas; reintento/backoff (reusa el §4
    de [[rama-judicial-actuaciones]]). Si un documento falla, **sigue con los demás** y lo reporta.
  - Devuelve `{ importados, omitidos, fallidos }`.
- **Por qué on-demand y no en el cron**: importar todos los expedientes en cada barrido sería N×M
  requests pesados (binarios) → costo y rate-limit. El cron solo trae *metadatos* de actuaciones; los
  PDFs se bajan cuando el abogado los pide.

### 4.3 Endpoints
- `GET  /procesos/:id/rama/documentos` (requirePermiso `proceso.ver`) → lista con `yaImportado`.
- `POST /procesos/:id/rama/documentos/importar` (requirePermiso `proceso.editar`) `{ idRegs?: string[] }`
  → ejecuta la importación; responde el resumen.

## 5. UI (ficha)

### 5.1 Subsección "Documentos del expediente (Rama)" dentro del panel del juzgado
```
 Documentos del expediente 🏛️                         [ Ver disponibles ↻ ]
 ─────────────────────────────────────────────────────────────────────────
 ☑ 09-mar  Certificación bancaria parte demandante          (nuevo)
 ☑ 03-mar  Auto que ordena entrega de títulos               (nuevo)
 ☐ 25-feb  Constancia constitución título judicial    ya en el proceso ✓
                                          [ Importar seleccionados (2) ]
 Importando… 2/2 · 1 listo · 0 con error
```
- "Ver disponibles" llama `GET …/rama/documentos` (lista, sin bajar binarios).
- Checkboxes (los `yaImportado` salen deshabilitados con "✓").
- "Importar seleccionados" → `POST …/importar`; barra de progreso (el endpoint puede responder al
  final con el resumen, o se hace por tandas para mostrar avance).
- Al terminar, los importados aparecen también en el panel **Documentos** del proceso con chip "del juzgado".

### 5.2 Atajo desde el timeline (correlación)
- En cada actuación con `conDocumentos`, un ícono 📎 y "ver documentos" que filtra la lista a los de esa
  actuación (`consActuacion`).

## 6. Casos borde / decisiones
- **Reservado / no publicado** → no hay documentos (mensaje claro, no error).
- **Documento no-PDF o muy grande** → se omite con aviso ("no se pudo traer: tipo/size"), el resto sigue.
- **Re-importar** → idempotente (no duplica) gracias al `@@unique`.
- **Permisos/RBAC** → importar exige `proceso.editar` (escribe documentos); ver, `proceso.ver`.
- **Almacenamiento** → reusa tecnovapp ([[reestructura-almacenamiento-documentos]]); carpeta
  `{tenant}_PROCESOS`, nombre = descripción del documento; categoría inferida por `categoriaDoc`.
- **Legal** → son documentos públicos del expediente; guardarlos en el proceso del despacho es correcto.
- **Cantidad** → si hay muchos, ofrecer "importar todos" con confirmación + progreso (puede tardar por
  el espaciamiento anti-bloqueo).

## 7. Esfuerzo y fases
- **Backend:** `getBuffer` en el transporte + `obtenerDocumentos`/`descargarDocumento` + servicio +
  2 endpoints + 1 campo de modelo. Medio-alto.
- **Frontend:** subsección de lista/selección/progreso + chip "del juzgado" + atajo 📎. Medio.
- **Sugerencia de fase:** (1) `GET …/rama/documentos` + lista solo-lectura con "ya importado"; luego
  (2) la descarga/importación con progreso. Permite entregar valor incremental.

## 8. Preguntas abiertas (para decidir al implementar)
1. ¿Importación **selectiva** (checkboxes) o "importar todo" de un botón? (Recomendado: ambos; default selectivo.)
2. ¿La categoría de los importados se infiere por nombre (`categoriaDoc`) o se marca todo como `AUTO`/`OTRO`?
   (Recomendado: `categoriaDoc`, ya existe.)
3. ¿Mostrar los documentos de la Rama **embebidos** (visor PDF) o solo enlace de descarga?
   (v1: enlace `construirUrlDocumento`; visor embebido más adelante.)
4. ¿Coordinar con la sesión paralela del *uploader de documentos* para reusar su componente al renderizar
   los importados? (Sí — evita duplicar UI de documentos.)
