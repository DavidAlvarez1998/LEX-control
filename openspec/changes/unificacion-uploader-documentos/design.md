# Diseño — unificacion-uploader-documentos

## Tres componentes, tres casos (regla)

| Caso | Componente | Cuándo |
|---|---|---|
| 1 documento con nombre fijo (poder.pdf, demanda.pdf…) | `BotonSubirDoc` | clave de documento conocida; gatea una etapa |
| N documentos con nombre libre | `DocumentosUploader` | el usuario decide cuántos y cómo se llaman |
| Adjuntar por enlace + generar desde plantillas | `DocumentosProceso` | expediente del proceso (no sube binarios) |

## `DocumentosUploader` — dos modos

Un solo componente cubre los dos contextos porque el quiebre real es **cuándo existe la entidad**:

- **Pendiente** (`value` + `onChange`): el proceso/contrato aún no existe (form de creación). Se
  acumulan `{ id, nombre, file }` en estado del padre; el nombre se autocompleta del archivo y es
  editable; el padre los sube **después de crear** la entidad. Muestra filas con nombre editable +
  chip del archivo (✓ nombre · tamaño) + reemplazar/quitar.
- **En vivo** (`existentes` + `subir` + `quitar`): la entidad ya existe. Al soltar/elegir archivos se
  **suben al instante** (secuencial), con el nombre del archivo; se listan los `existentes`
  (nombre + `sub` opcional + Ver + Quitar con confirmación). `extra` permite inyectar campos sobre el
  dropzone (la categoría del contrato).

Detección de modo: `live = !!subir`.

### Por qué "subir al instante" en vivo (no pending+botón)
Decisión del usuario. Menos fricción para el caso común (soltar y listo). Se pierde el renombrado
previo, aceptado a cambio de simplicidad; el nombre queda como el del archivo.

## Admin vs client (copias espejo)
Los dos portales tienen librerías de UI distintas (client = primitivas slate-* + `form-ui`/`ConfirmDialog`;
admin = tokens semánticos `bg-subtle`/`text-foreground`/`text-accent` + `Modal`). Siguiendo la
convención de componentes espejo del repo, hay **dos archivos** `documentos-uploader.tsx`:
- client: ambos modos (pendiente lo usa el form de creación).
- admin: solo modo en vivo (su único consumidor son los contratos).

## `AdjuntosLibres` como wrapper
Se conserva como API estable para no tocar `datos-proceso.tsx`. Internamente:
- `existentes` = docs del proceso filtrados por `prefix`, mapeados a `{ id, nombre: sinPrefijo, url }`.
- `subir(file)` = `subirArchivoProceso(procesoId, file, prefix + file.name)` → `onSubido(doc)`.
- `quitar(id)` = `eliminarDocumento(procesoId, id)` → `onEliminado(id)`.
El agrupado por `prefix` (p. ej. `"audiencia: "`) sigue intacto.

## Errores
El uploader muestra el error **inline** (un solo lugar). `DocumentosContrato.onError` se vuelve
opcional y deja de usarse para no duplicar el mensaje en la página.

## No-objetivos
- No se añade soporte real de `<input multiple>` en el backend (sigue 1 archivo/request).
- No se migra `DocumentosProceso` (enlace + plantillas).
