# Tasks

## 1. Catalog (seed-tipos.json — Derecho de Petición Recibido)
- [x] 1.1 "Respuesta" stage: add `medioRespuesta` to `camposRequeridos` for `contestada = SI` and `= PARCIAL`.
- [x] 1.2 "Respuesta" stage: add optional documents by channel — `medioRespuesta = "Correo electrónico"` → `acuse-correo.pdf`; `medioRespuesta = "Físico"` → `constancia-envio.pdf`.

## 2. Client
- [x] 2.1 `DOC_ETIQUETAS`: `acuse-correo` → "Acuse de correo", `constancia-envio` → "Constancia de envío".
- [x] 2.2 BUGFIX `DatosProceso`: document upload panels were anchored to `requierePoder`/`contestaron` (sent-DdP keys), so for the Recibido (`contestada`, no `requierePoder`) the `respuesta.pdf` uploader never rendered. Anchor now picks the field that exists: base → `requierePoder`|`queSolicita`; response → `contestaron`|`contestada`. `neutro` also resets `medioRespuesta` so the channel acuse classifies as a response doc.

## 3. Verify
- [x] 3.1 `pnpm seed:catalogo`; API + client `tsc` clean.
- [x] 3.2 Smoke e2e (scripts/smoke-peticion-flow.ts): contestar SI sin medioRespuesta → 400; con medio → avanza; plantilla respuesta renderiza.

## 4. Archive
- [x] 4.1 Merge delta into `openspec/specs/tramite-management/spec.md`; move to `archive/`.
