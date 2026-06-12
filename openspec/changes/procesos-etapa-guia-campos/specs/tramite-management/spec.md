# Tramite Management — delta (blocked stage guides to the inputs)

> Change `procesos-etapa-guia-campos`. Extends `tramite-management` presentation: a stage transition
> blocked by missing inputs now guides the user to where they are completed (the form for fields, the
> documentos-requeridos panel for documents) and marks each missing field in place, instead of only
> printing a list of field keys. The server-side stage gate (`PATCH /procesos/:id/etapa` returning
> `400 { faltantes, documentosFaltantes }`) is UNCHANGED.

## ADDED Requirements

### Requirement: A field-blocked stage transition opens and marks the form
When the user clicks a stage and the move is rejected because required FIELDS are missing (the `400`
`faltantes`), the ficha MUST scroll to the proceso form, put it in edit mode, and visually mark each
missing field (required-asterisk + per-field error state) by passing the missing field keys to the
form. The marks MUST clear per-field as each one receives a value (the highlight is filtered against
the current draft). A short pointer message MUST replace the raw key list. This applies to any
`TipoProceso` (DdP, tutela, judicial).

#### Scenario: DdP radicación block opens the form with both fields marked
- GIVEN a DdP whose `radicada` stage requires `fechaRadicacion` and `nroRadicado`, both empty
- WHEN the lawyer clicks the `radicada` stage
- THEN the view scrolls to the form, the form is in edit mode, and `fechaRadicacion` and `nroRadicado`
  are marked as required/missing

#### Scenario: A marked field clears as it is filled
- GIVEN the form is showing `nroRadicado` marked as missing
- WHEN the lawyer types a value into `nroRadicado`
- THEN that field's missing mark clears while still-empty required fields stay marked

#### Scenario: Tutela behaves the same
- GIVEN a tutela stage requiring fields that are empty
- WHEN the lawyer clicks that stage
- THEN the form opens and each missing field is marked (same mechanism, no type-specific code)

### Requirement: A document-blocked stage transition highlights the documentos panel
When the move is rejected because required DOCUMENTS are missing (the `400` `documentosFaltantes`),
the ficha MUST scroll to and visually highlight the "Documentos requeridos" panel (where the missing
documents are listed for upload), with a short message naming them, rather than printing the raw list
under the stage only.

#### Scenario: Missing poder.pdf routes to the requeridos panel
- GIVEN a DdP whose next stage requires `poder.pdf` and it is not attached
- WHEN the lawyer clicks that stage
- THEN the view scrolls to and highlights the "Documentos requeridos" panel listing `poder.pdf`

#### Scenario: Mixed field+document block guides to both
- GIVEN a stage that requires both a missing field and a missing document
- WHEN the lawyer clicks it
- THEN missing fields are marked in the form and the documentos-requeridos panel is highlighted
