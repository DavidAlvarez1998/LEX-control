# Almacenamiento Documental (tecnovapp) Specification

> Patrón transversal y CANÓNICO para subir archivos en LEX Control. TODA capacidad que suba documentos (contratos, poderes/expedientes de procesos, y las futuras) DEBE seguir este patrón: el binario vive en un microservicio documental EXTERNO (tecnovapp); en nuestra BD guardamos únicamente la `path` relativa que devuelve, y la URL pública se RECONSTRUYE al leer. Referencia de implementación viva: `lex-control-api/src/modules/documentos/documentos.client.ts` y el módulo de contratos (`contratos.router.ts`, primer adoptante). Ver también `openspec/roadmap-docs/APIs/API-DOCUMENTOS-INTEGRACION (1).md`.
>
> **Estructura de carpetas (2026-06-20):** tecnovapp solo permite UN nivel de carpeta — la ruta es FIJA `{EMPRESA}/{CARPETA}/{AÑO}/{MES}/{archivo}` (el server agrega AÑO/MES y pasa a MAYÚSCULA; un 3er segmento da 404 y un "/" interno se vuelve "_"). Se usa una **raíz paraguas única por producto** (estilo doc §7, ej. `FINOVA/…`): la RAÍZ `{EMPRESA}` = `env.documentos.raizPrefijo` (`DEMO-LEXCONTROL` / `LEXCONTROL`), y como solo hay un nivel libre, la `{CARPETA}` combina **tenant + módulo**: `carpetaModulo(empresa, modulo)` = `{tenant}_{modulo}`, con `tenant` = `ADMIN` (plataforma) o `{slug-nombre}-{empresaId}` (despacho). Así todo el producto queda bajo UNA raíz y los despachos quedan aislados por el prefijo del nombre de carpeta (ordenan juntos). El id de la entidad va en `documento` (→ nombre del archivo). El detalle por proceso/contrato/cliente NO se modela en carpetas: vive en la BD (relaciones).
>
> Ej.: `DEMO-LEXCONTROL / BUFETE-PEREZ-CL9A_PROCESOS / 2026 / 06 / 1781..._poder.pdf` · `DEMO-LEXCONTROL / ADMIN_USUARIOS / …`

## ADDED Requirements

### Requirement: El binario vive en tecnovapp; la BD guarda solo la `path`
El sistema NO almacena los binarios de los archivos ni en la base de datos ni en disco local. El binario se sube a un microservicio documental externo (tecnovapp) vía su API, y en la BD se persiste ÚNICAMENTE la `path` relativa que el servicio devuelve (forma `{EMPRESA}/{CARPETA}/{YYYY}/{MM}/{filename}`). NO se persiste la URL absoluta: así un cambio de dominio (o de DEMO a producción) no rompe los registros existentes.

#### Scenario: Tras subir, solo se guarda la path
- GIVEN un archivo subido al microservicio
- WHEN el módulo registra el documento en BD
- THEN se guarda la `path` relativa devuelta (no el binario, no la URL absoluta)

#### Scenario: El dominio puede cambiar sin migrar datos
- GIVEN documentos guardados con su `path` relativa
- WHEN cambia `env.documentos.apiUrl` (p. ej. DEMO → producción)
- THEN las URLs públicas se reconstruyen contra el nuevo dominio sin tocar la BD

### Requirement: Todo acceso al microservicio pasa por documentos.client.ts
Ningún módulo de negocio habla con `fetch` directo contra tecnovapp. Toda subida usa `subirDocumento(params)` y toda lectura reconstruye la URL con `construirUrlDocumento(path)`, ambos de `src/modules/documentos/documentos.client.ts`. Así, cambiar de proveedor o de entorno es tocar solo `env.documentos`, no los módulos.

#### Scenario: Subida centralizada
- GIVEN un módulo que necesita subir un archivo
- WHEN implementa la subida
- THEN invoca `subirDocumento(...)` y NO hace `fetch` directo al microservicio

#### Scenario: Lectura centralizada
- GIVEN una `path` guardada en BD
- WHEN se sirve el documento al frontend
- THEN la URL pública se obtiene con `construirUrlDocumento(path)` (tolera path relativa, path con "/" inicial, o URL ya absoluta; devuelve null si no hay path)

### Requirement: Contrato de subirDocumento y configuración por entorno
`subirDocumento` recibe `{ archivo: Buffer|Uint8Array, nombreArchivo, documento, carpeta, tipo? }` y devuelve `{ path, filename, url }`. La RAÍZ `{EMPRESA}` la pone internamente `subirDocumento` desde `env.documentos.raizPrefijo` (paraguas único); `carpeta` es el único nivel libre y SIEMPRE se construye con `carpetaModulo(empresa, modulo)` = `{tenant}_{MÓDULO}` (nunca a mano), con módulo en MAYÚSCULA (`"CONTRATOS"`, `"PROCESOS"`, …); `documento` es el identificador del dueño (cédula, NIT, código de proceso). La base URL y el timeout salen de `env.documentos` (`apiUrl`, `timeoutMs`). El microservicio antepone un timestamp al `filename`.

#### Scenario: La path incluye paraguas, tenant_módulo y fecha
- GIVEN una subida de un proceso de la empresa `{id, nombre}` con `carpetaModulo(empresa, "PROCESOS")`
- WHEN el servicio responde
- THEN la `path` tiene la forma `{raizPrefijo}/{slug}-{id}_PROCESOS/{YYYY}/{MM}/{filename}`

#### Scenario: Fallo del microservicio no confirma a medias
- GIVEN el microservicio no responde a tiempo o responde con error
- WHEN se intenta subir
- THEN `subirDocumento` lanza `HttpError(502)` y el módulo NO crea el registro en BD

### Requirement: Endpoint de subida multipart estándar
Una capacidad que sube archivos expone un endpoint multipart con `multer` en memoria (`memoryStorage`, límite 15 MB), gateado por `requireAuth` + el `requirePermiso` concreto de esa capacidad, que: valida la propiedad del recurso (mismo `empresaId` del token), exige `req.file`, llama a `subirDocumento(...)` con la `carpeta` del módulo, crea la fila de documento guardando la `path`, y responde con el documento incluyendo su `url` pública (vía `construirUrlDocumento`). El `empresaId` SIEMPRE sale del token, nunca del cliente.

#### Scenario: Subida autorizada y aislada por tenant
- GIVEN un usuario con el permiso de escritura de la capacidad
- WHEN sube un archivo a un recurso de SU empresa
- THEN el binario va a tecnovapp, se crea la fila con la `path`, y la respuesta trae la `url` pública

#### Scenario: Recurso de otra empresa
- GIVEN un usuario de la empresa A
- WHEN intenta subir a un recurso de la empresa B
- THEN el endpoint responde 404/403 y no se sube nada

#### Scenario: Sin archivo
- GIVEN una petición multipart sin parte `file`
- WHEN llega al endpoint
- THEN responde `400` sin tocar el microservicio

### Requirement: La columna de ruta puede llamarse `path` o reutilizar `url`
Cada modelo de documento guarda la ruta en una columna string. Los modelos nuevos usan `path` (como `DocumentoContrato`). Modelos preexistentes cuya columna `url` ya admitía "enlace o ruta" (como `DocumentoProceso`) pueden almacenar ahí la `path` de tecnovapp para los archivos subidos y un enlace absoluto para los adjuntos por enlace; en ambos casos la serialización pasa el valor por `construirUrlDocumento`, que es tolerante. NO se exige migrar la columna por consistencia cosmética.

#### Scenario: DocumentoProceso reutiliza url para la path
- GIVEN un poder subido a un proceso
- WHEN se guarda
- THEN la `path` de tecnovapp queda en `DocumentoProceso.url` y al leer el proceso ese valor se sirve resuelto por `construirUrlDocumento`

#### Scenario: Adjunto por enlace coexiste con archivo subido
- GIVEN un documento adjuntado por enlace (URL absoluta) y otro subido (path relativa) en el mismo expediente
- WHEN se serializa la lista de documentos
- THEN ambos exponen una `url` pública correcta (la URL absoluta pasa intacta; la path relativa se prefija con la base)

### Requirement: Metadata del documento y relaciones por la BD
La fila del documento guarda metadata intrínseca: `categoria` (clase del documento — para `DocumentoProceso` el enum `CategoriaDocumentoProceso`: DEMANDA/PODER/PRUEBA/ANEXO/AUTO/SENTENCIA/IMPUGNACION/GENERADO/OTRO; para `DocumentoContrato` el enum existente), `tipo` (mime) y `subidoPorId` (auditoría: quién subió). NO se duplican en el documento los datos del padre (cliente, juzgado/radicado, abogado, despacho, partes): se alcanzan vía `procesoId`→`Proceso` (o `contratoId`→`Contrato`). Las consultas ("docs de un proceso/cliente/juzgado/usuario", "solo los poderes") se resuelven en la BD, no navegando carpetas. El gating de etapa (`documentosRequeridos`) sigue siendo por `nombre`; `categoria` es metadata complementaria que se infiere del nombre/slot al subir (los documentos generados desde plantilla son `GENERADO`).

#### Scenario: Filtrar por clase de documento
- GIVEN documentos de un proceso con distintas `categoria`
- WHEN se piden solo los poderes
- THEN `WHERE procesoId = X AND categoria = PODER`

#### Scenario: Datos del proceso sin denormalizar
- GIVEN un documento de proceso
- WHEN se necesita su cliente o juzgado
- THEN se obtienen por la relación `procesoId`→`Proceso`, sin copiarlos en el documento
