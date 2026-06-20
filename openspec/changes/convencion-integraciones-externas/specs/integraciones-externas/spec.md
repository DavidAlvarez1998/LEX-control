# Integraciones Externas (consumo de APIs de terceros) Specification

> Patrón transversal y CANÓNICO para consumir servicios HTTP de terceros (gobierno, validación de
> datos, pasarelas de pago, etc.) en LEX Control. TODA capacidad que llame a una API externa DEBE
> seguir este patrón. Es el equivalente, para *consumir* servicios, de lo que [[documental-storage]]
> es para *subir archivos*. Referencia de implementación viva:
> `lex-control-api/src/modules/documentos/documentos.client.ts`.

## ADDED Requirements

### Requirement: Todo `fetch` a un tercero vive en `<nombre>.client.ts`
Ningún módulo de negocio, router, repository ni componente del front hace `fetch` directo contra una
API de tercero. Cada integración aísla TODA su comunicación externa en un único archivo
`src/modules/<nombre>/<nombre>.client.ts`. Cambiar de proveedor, de versión de su API o de entorno
(DEMO → producción) DEBE costar tocar solo ese archivo y su bloque `env`, nunca los módulos que lo
usan.

#### Scenario: Comunicación externa centralizada
- GIVEN un módulo de negocio que necesita datos de un tercero
- WHEN implementa la llamada
- THEN invoca una función del `<nombre>.client.ts` y NO hace `fetch` directo al tercero

#### Scenario: Cambiar de entorno sin tocar negocio
- GIVEN una integración apuntando al entorno DEMO del proveedor
- WHEN se cambia `env.<nombre>.baseUrl` a producción
- THEN el negocio y los routers no se modifican

### Requirement: El cliente normaliza la respuesta a un DTO propio
El `<nombre>.client.ts` traduce la respuesta del tercero a un DTO definido en `<nombre>.types.ts`,
independiente del esquema del proveedor. El negocio y el front consumen SOLO la forma normalizada,
nunca el JSON crudo del tercero. La normalización es tolerante a campos faltantes (valores por
defecto / null), no asume nombres de campo del proveedor fuera del client.

#### Scenario: El negocio no se acopla al esquema del tercero
- GIVEN dos proveedores distintos para el mismo dato
- WHEN cada client normaliza su respuesta
- THEN ambos devuelven el mismo DTO y el resto del sistema no distingue cuál se usó

### Requirement: Conexiones y secretos solo en `env`, nunca en código ni en git
La URL base, las llaves/tokens y los timeouts de cada tercero se leen de `env.<nombre>` en
`src/config/env.ts`, que a su vez los toma de variables de entorno (`.env`, que NO se commitea). Está
prohibido hardcodear URLs de producción o credenciales en el código fuente. Una llave secreta nunca
se registra en logs ni se devuelve al front.

#### Scenario: Sin secretos en el repositorio
- GIVEN una integración con API key
- WHEN se revisa el código fuente versionado
- THEN la key no aparece; solo `process.env.<X>` leído en `env.ts`, con valor real en `.env`

#### Scenario: Default seguro de entorno
- GIVEN una variable de entorno opcional no seteada
- WHEN arranca la API
- THEN se usa un default no sensible (p. ej. host público), y las variables obligatorias se exigen al boot

### Requirement: Resiliencia — timeout y fallo aislado, sin confirmar a medias
Toda llamada externa usa un timeout (`AbortController`) y traduce cualquier fallo del tercero (caído,
lento, status no-OK, formato inesperado) a `HttpError(502)` con un mensaje legible. Un tercero caído
NO debe colgar la request ni dejar una operación a medias: si una mutación depende de la llamada
externa y ésta falla, NO se persiste el cambio local.

#### Scenario: Tercero no responde a tiempo
- GIVEN una API externa que excede `env.<nombre>.timeoutMs`
- WHEN se la consulta
- THEN el client aborta y lanza `HttpError(502)` con mensaje claro, sin colgar la request

#### Scenario: Mutación dependiente no queda inconsistente
- GIVEN una operación que primero llama al tercero y luego escribe en BD
- WHEN la llamada externa falla
- THEN no se escribe nada en BD y se devuelve el error al cliente

### Requirement: El endpoint propio se expone con auth, permiso y aislamiento por tenant
Cada integración se expone a los portales mediante un router propio montado en `app.ts`
(`app.use("/<ruta>", <nombre>Routes)`), gateado por `requireAuth` y el `requirePermiso` que
corresponda. La entrada (params/body/query) se valida con zod (`<nombre>.schemas.ts`). El `empresaId`
SIEMPRE sale del token, nunca del cliente. El front consume este endpoint propio; jamás se expone la
URL ni la llave del tercero al navegador.

#### Scenario: Acceso autorizado
- GIVEN un usuario sin el permiso requerido
- WHEN llama al endpoint de la integración
- THEN responde 403 y no se llama al tercero

#### Scenario: La llave del tercero nunca llega al navegador
- GIVEN una integración con credencial
- WHEN el front consume el dato
- THEN la request va a nuestro endpoint (`/api/...`) y la credencial queda solo en el backend

#### Scenario: Entrada inválida
- GIVEN parámetros que no cumplen el schema zod
- WHEN llegan al endpoint
- THEN responde 400 con los issues, sin llamar al tercero

### Requirement: El front consume solo nuestro endpoint vía `lib/<nombre>-api.ts`
En cada portal, el acceso a la integración se encapsula en `src/lib/<nombre>-api.ts`, que usa el
helper `api` (`api.get/post/patch/del` de `lib/api.ts`) contra nuestra ruta. Los componentes importan
ese módulo y manejan errores con `errorMessage(...)`. Ningún componente arma URLs del tercero ni
llama a `fetch` crudo a un servicio externo.

#### Scenario: Consumo encapsulado
- GIVEN un componente que muestra un dato de la integración
- WHEN lo solicita
- THEN llama a una función de `lib/<nombre>-api.ts` (que usa `api.get`), no a `fetch` directo

### Requirement: Persistencia de datos del tercero (cuando aplique) — tenant, idempotencia y habeas data
Si la integración guarda datos traídos del tercero, se modela en Prisma con `<nombre>.repository.ts`
tenant-scoped (`empresaId` desnormalizado o resuelto desde el recurso dueño). La sincronización es
idempotente (clave/hash que evita duplicados al re-sincronizar). Los datos personales se rigen por
Ley 1581/2012 ([[compliance-habeas-data]]): existe base lícita y se borran junto con el recurso
dueño. Las credenciales por despacho, si las hay, se guardan cifradas (nunca en texto plano).
Consultas repetidas pueden servirse de caché dentro de un TTL configurable.

#### Scenario: Re-sincronizar no duplica
- GIVEN datos ya traídos del tercero y persistidos
- WHEN se vuelve a sincronizar lo mismo
- THEN no se crean filas duplicadas (idempotencia por clave/hash)

#### Scenario: Aislamiento entre despachos
- GIVEN datos sincronizados para un recurso del despacho B
- WHEN un usuario del despacho A los solicita
- THEN responde 404 y no ve datos de otro tenant

#### Scenario: Borrado por habeas data
- GIVEN un recurso con datos personales traídos del tercero
- WHEN el despacho borra el recurso
- THEN sus datos sincronizados se eliminan también

### Requirement: Cada integración real se documenta como su propio change OpenSpec
Antes de implementar una API externa concreta se crea un change que referencia esta convención y
añade su capacidad específica (proveedor, endpoints, modelos, env vars). No se implementa una
integración "suelta" sin spec. Una integración que se retira se documenta con un change de remoción
(como [[remove-integraciones-estatales]]).

#### Scenario: Trazabilidad de una integración
- GIVEN una nueva API externa a incorporar
- WHEN se planifica
- THEN existe un change OpenSpec propio que cumple `integraciones-externas` y describe su especificidad
