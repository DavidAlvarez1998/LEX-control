# inventario-puntos-subida-archivos

## Por qué

Inventario (auditoría, 2026-06-22) de **todos los puntos del proyecto donde se suben archivos**,
para tener un mapa único antes de cualquier unificación/refactor.

## Hallazgo clave (transversal)

- **No existe ningún `<input multiple>`**: ningún punto sube varios archivos en una sola petición.
- El backend **siempre recibe UN archivo por request** (`multer.upload.single("file")`).
- "Subir varios archivos" se resuelve en el front **subiendo de a uno** y armando una lista.
- Todos los puntos de subida viven en **`lex-control-client`** (salvo `DocumentosContrato`,
  que también existe en `lex-control-admin`).

## Mecanismos de subida (front)

### A) Archivo ÚNICO — `BotonSubirDoc`
Componente: `lex-control-client/src/components/boton-subir-doc.tsx` (botón + modal, 1 doc por clave fija).
Usos:
- `lex-control-client/src/components/datos-proceso.tsx:127` — documentos requeridos de la ficha
- `lex-control-client/src/app/(dashboard)/procesos/nuevo/page.tsx:230` — poder/doc inicial
- `lex-control-client/src/app/(dashboard)/procesos/nuevo/page.tsx:267` — documento de prueba
- `lex-control-client/src/app/(dashboard)/procesos/nuevo/page.tsx:299` — documento de cautelares

### B) VARIOS archivos (N, uno a uno, nombre libre) — `AdjuntosLibres`
Componente: `lex-control-client/src/components/adjuntos-libres.tsx` (sube N docs agrupados por `prefix`).
Usos:
- `lex-control-client/src/components/datos-proceso.tsx:317` — adjuntos libres por sección de la ficha

### C) Gestores de lista con formulario de carga (adicionales)
- **`DocumentosContrato`** — `documentos-contrato.tsx` (existe en admin y client):
  - `lex-control-client/src/app/(dashboard)/cuenta/page.tsx:236`
  - `lex-control-client/src/app/(dashboard)/contratos/page.tsx:536`
  - `lex-control-admin/src/components/contratos-comercial.tsx:446`
- **`DocumentosProceso`** — `lex-control-client/src/components/documentos-proceso.tsx`:
  - `lex-control-client/src/app/(dashboard)/procesos/[id]/page.tsx:496`

## Backend (endpoints multer)

- `POST /procesos/:id/documentos/subir` — `lex-control-api/src/modules/procesos/procesos.router.ts:94` — `upload.single("file")`
- `POST /contratos/:id/documentos` — `lex-control-api/src/modules/contratos/contratos.router.ts:46` — `upload.single("file")`

Helpers cliente que arman el `FormData`: `subirArchivoProceso` (`lib/procesos-api.ts:282`)
y `uploadFile` (`lib/api.ts`) usado por `DocumentosContrato`.

## Qué cambia

Nada de código. Solo inventario/documentación. Sirve de base para una eventual unificación
(p. ej. un único componente de subida o soporte real de `multiple`).

> **Seguimiento:** la unificación de los casos de N archivos se implementó en el change
> `unificacion-uploader-documentos` (componente estándar `DocumentosUploader`, 2026-06-22).
