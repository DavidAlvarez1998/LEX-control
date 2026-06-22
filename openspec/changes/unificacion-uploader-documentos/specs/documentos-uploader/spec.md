# spec — uploader estándar de documentos

Comportamiento canónico de la subida de documentos en los portales. Reusa los endpoints multer
existentes (un archivo por request); no introduce transporte propio ni `<input multiple>` de servidor.

## Selección de componente (regla)

| Caso | Componente |
|---|---|
| **1 documento con nombre/clave fija** (gatea una etapa: poder.pdf, demanda.pdf, constancia-radicado.pdf…) | `BotonSubirDoc` |
| **N documentos con nombre libre** (el usuario decide cuántos) | `DocumentosUploader` |
| **Expediente: adjuntar por enlace + generar desde plantillas** | `DocumentosProceso` |

## `DocumentosUploader` — contrato

Dos modos, excluyentes, según exista o no la entidad destino:

### Modo pendiente (form de creación)
- Props: `value: { id, nombre, file }[]`, `onChange(next)`.
- Recoge los `File` en memoria. El nombre se **autocompleta** con el del archivo (sin extensión) y es
  **editable**. El padre sube los archivos **después de crear** la entidad.
- Cada fila muestra: nombre editable, chip del archivo (✓ nombre · tamaño) y acciones reemplazar/quitar.
- No sube nada por sí mismo.

### Modo en vivo (entidad existente)
- Props: `existentes: { id, nombre, url?, sub? }[]`, `subir(file): Promise`, `quitar(id): Promise`,
  `extra?` (ReactNode sobre la zona de carga).
- Al soltar/elegir uno o más archivos se **suben al instante** (secuencialmente, con estado "Subiendo…").
  El nombre del documento es el del archivo.
- Lista los `existentes` con enlace **Ver** (si hay `url`), subtítulo `sub` opcional, y **Quitar** con
  diálogo de confirmación.
- Los errores de subir/quitar se muestran **inline** en el propio componente.

### Común
- Zona de **arrastrar/soltar o elegir** (acepta varios a la vez).
- `titulo`, `descripcion`, `opcional` (decora el título), `readOnly` (oculta carga y quitar).

## Garantías / invariantes

- **Un archivo por request.** Aunque se suelten varios, se suben de a uno a los endpoints existentes.
- **El agrupado por sección se mantiene** vía prefijo en el nombre (`AdjuntosLibres` usa `prefix`,
  p. ej. `"audiencia: "`), de modo que cada sección lista solo sus documentos.
- **`BotonSubirDoc` no cambia**: sigue cubriendo el documento con clave fija que valida una etapa.
- **`DocumentosProceso` no sube binarios**: adjunta por enlace/URL y genera desde plantillas; queda
  fuera de este estándar.
- **Sin cambios de backend ni de la forma del `FormData`** (`file`, y `nombre`/`categoria`/`tipo`
  según el endpoint).

## Casos cableados

- Form de crear proceso (ejecutivo): "Documentos de prueba" y "Documentos de medidas cautelares"
  (este último solo si `solicitaCautelares = Sí`, anclado bajo `otrasCautelares`) — modo pendiente.
- Ficha de proceso: `AdjuntosLibres` por sección — modo en vivo.
- Contratos (client `/cuenta` y `/contratos`; admin gestión) — modo en vivo + categoría como `extra`.
