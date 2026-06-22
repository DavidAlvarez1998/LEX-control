# unificacion-uploader-documentos

## Por qué

El inventario [[inventario-puntos-subida-archivos]] dejó el mapa de todos los puntos de subida y
anticipó "una eventual unificación (un único componente de subida)". Cada punto de N archivos tenía
su propio bloque ad-hoc (form de creación, ficha de proceso, contratos en admin y client), con UX
dispar (una fila vacía → teclear nombre → modal por archivo). Se unifica en **un componente estándar**
con mejor UX (arrastrar/soltar, autocompletar nombre, chip con tamaño) reutilizado en todos los casos
de N archivos.

Decisión del usuario (2026-06-22): estandarizar **todos** los casos de N archivos (ficha + contratos,
admin y client) y, en las subidas a una entidad ya existente, **subir al instante** (sin paso previo
de nombres; el nombre = nombre del archivo).

## Qué cambia

- **Nuevo `DocumentosUploader`** (componente estándar de N documentos) con **dos modos**:
  - **Pendiente** (form de creación, la entidad aún no existe): controlado `value`/`onChange`; junta
    los `File` en memoria con nombre editable (autocompletado); el padre los sube al crear.
  - **En vivo** (entidad existente): `existentes` + `subir(file)` (sube al instante) + `quitar(id)`
    + `extra` (ReactNode sobre el dropzone, p. ej. selector de categoría).
- **Migrados** al estándar:
  - Form de crear proceso: "Documentos de prueba" y "Documentos de medidas cautelares" (modo pendiente).
  - `AdjuntosLibres` (ficha de proceso) → wrapper delgado del estándar en modo en vivo; **API pública
    intacta** (procesoId/docs/prefix/onSubido/onEliminado/readOnly), no se tocan call sites.
  - `DocumentosContrato` (client y admin) → estándar en modo en vivo + categoría como `extra`.
- **Sin cambios**:
  - `BotonSubirDoc` sigue siendo el estándar del caso **1 documento con nombre fijo**.
  - `DocumentosProceso` (ficha) **no se migra**: no sube archivos, adjunta por **enlace/URL** + genera
    desde plantillas (otro paradigma; migrarlo exigiría endpoint multer nuevo).
- **Sin cambios de backend**: se reusan los endpoints multer existentes
  (`POST /procesos/:id/documentos/subir`, `POST /contratos/:id/documentos`) y los helpers
  `subirArchivoProceso` / `uploadFile`. Sigue siendo **un archivo por request**.

## Impacto

- Componentes nuevos: `lex-control-client/src/components/documentos-uploader.tsx`,
  `lex-control-admin/src/components/documentos-uploader.tsx` (espejo con tokens del admin).
- Modificados: `adjuntos-libres.tsx`, `documentos-contrato.tsx` (×2), `procesos/nuevo/page.tsx`.
- `DocumentosContrato.onError` queda opcional/no usado (los errores se muestran inline en el uploader).
- Catálogo (datos): en "Proceso ejecutivo de mínima cuantía" el doc `solicitud-cautelares.pdf` pasó a
  opcional condicional (`opcionalesSi` con `si: solicitaCautelares=Sí`) y se ancla bajo
  `otrasCautelares` (nuevo soporte `anclaCampo` en `opcionalesSi`). Ver [[proceso-ejecutivo-minima-cuantia]].
