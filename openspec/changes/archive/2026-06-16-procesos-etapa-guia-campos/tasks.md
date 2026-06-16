# Tasks — procesos-etapa-guia-campos

Client-only presentation change. Reuses the existing 400 `{ faltantes, documentosFaltantes }`, the
`FormularioDinamico.errores` prop, and `DatosProceso` edit mode. No API/schema/gate change.

## Ficha (procesos/[id]/page.tsx)
- [x] `irAEtapa`: keep `faltantes` (campos) and `documentosFaltantes` SEPARATE (stop merging them)
- [x] On field-faltantes: set a `resaltarCampos` state with the keys and scroll to the form section
      (ref + `scrollIntoView`); on doc-faltantes: set a `resaltarDocs` flag and scroll to the
      documentos-requeridos panel
- [x] Replace the under-stage message: short pointer ("Completa abajo los campos marcados ↓" /
      "Faltan documentos: …, súbelos abajo") instead of the raw key list
- [x] Give the form Card and the documentos-requeridos panel an id/ref to scroll to

## DatosProceso (datos-proceso.tsx)
- [x] New prop `resaltarCampos?: string[]`; when non-empty, auto-enter edit mode
- [x] Compute `erroresVivos = resaltarCampos.filter(k => draft[k] is empty)` and pass as
      `errores` to `FormularioDinamico` so each missing field is marked and clears as filled

## DocumentosRequeridos (documentos-requeridos.tsx)
- [x] Optional `resaltar?: boolean` → ring/emphasis when the panel is the target of a doc-block

## Verify
- [x] `pnpm --dir lex-control-client build` (next) clean
- [x] Verified: backend gate contract `400 { faltantes, documentosFaltantes }` (the data the UI
      consumes) proven end-to-end vs real DB — `scripts/smoke-etapa-guia.ts` 7/7: DdP→radicada with
      empty fechaRadicacion/nroRadicado returns both as faltantes; one filled → only the other stays
      faltante (self-clearing premise); conditional poder.pdf by requierePoder; filled+attached → 200.
      Client wiring (resaltarCampos + scrollIntoView + edit mode + erroresVivos self-clear) confirmed by
      code-read + next build green. NOTE: docs route to the FORM (inline archivo fields), not a separate
      panel — spec delta reconciled to match. No real-browser screenshot (no playwright in repo).
