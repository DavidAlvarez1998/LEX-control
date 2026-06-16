# Proposal: Blocked stage → guide to the form fields, don't just list keys

## Intent
Today, when a lawyer clicks a stage (DdP or tutela) that is gated by missing required inputs, the
ficha answers with a red line under the stage: *"Para avanzar a esta etapa faltan: fechaRadicacion,
nroRadicado."* — a list of **field keys**, far from where they are filled, and offering no way to act.
The lawyer then has to scroll down, find the form, open it, and guess which fields those keys map to.

This change turns that dead-end message into **guidance**: when the block is due to missing **fields**,
the ficha scrolls to the proceso form, opens it in edit mode, and **marks each missing field** in
place (label asterisk + error state). When the block is due to missing **documents**, it scrolls to
and highlights the "Documentos requeridos" panel. The lawyer lands exactly on what to complete.

## Why this is coherent with the design (SDD validation)
Pure presentation, client-only. The server-side gate is **unchanged**: `PATCH /procesos/:id/etapa`
already returns `400` with `{ faltantes, documentosFaltantes }` (field keys + document names). The
`FormularioDinamico` already accepts an `errores` (keys) prop and renders per-field error state, and
`DatosProceso` already has an edit mode. This change only **wires** the existing 400 response to the
existing form-error mechanism, plus a scroll. No API, no schema, no gate/branch/vencimiento change.

## Scope
- **Ficha → on blocked transition by fields**: scroll to the proceso form, enter edit mode, pass the
  missing field keys as form errors so each one is marked; the marks clear per-field as the lawyer
  fills them. A short pointer message ("Completa abajo los campos marcados ↓") replaces the raw key
  list.
- **Ficha → on blocked transition by documents**: scroll to and highlight the "Documentos requeridos"
  panel (the missing docs already render there); keep a short message naming them.
- Split the currently-merged block info into fields vs documents so each routes to the right place.
- Works identically for DdP, tutela, and any type (the mechanism is generic).

## Decisions
- **Client-only.** Reuse the 400 payload, `FormularioDinamico.errores`, and `DatosProceso` edit mode.
- **Mark, then self-clear.** Missing fields are marked; as a field gets a value its mark clears live
  (filter the highlight list against the current draft), so the lawyer sees progress.
- **Fields → form, documents → requeridos panel.** Two destinations, matching where each is completed.
- **Keep a short message** for context, but the primary response is the scroll + in-place marking.

## Out of scope
- Auto-saving or auto-advancing after the fields are filled (the lawyer still clicks the stage again).
- Changing which fields/documents a stage requires (that is the catalog/gate, untouched).
- Highlighting individual missing documents beyond drawing attention to the panel.

## Rollback
Presentation-only: revert the `DatosProceso` highlight prop, the ficha's scroll/route logic, and the
documentos panel highlight. The server 400 and all gates are unchanged.
