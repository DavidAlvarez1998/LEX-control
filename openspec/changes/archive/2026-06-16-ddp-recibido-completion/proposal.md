# Proposal: Complete `Derecho de Petición Recibido` per the Juan David doc

## Intent
Close the remaining gaps between the **RECIBIR – DERECHO DE PETICIÓN** section of the source doc
(`openspec/roadmap-docs/DERECHO DE PETICIÓN - JUAN DAVID.docx`) and the implemented type. The reception
and response data are mostly modelled already; what the doc requires and we lack is the **proof of how the
response was sent** (acuse de correo / constancia física) and that the **send channel is captured when we
answer**.

## Audit (doc → implementation)
| Doc element (RECIBIR) | Field / rule | Status |
| --- | --- | --- |
| Radicado de ingreso (alfanumérico) | `radicadoIngreso` (auto) | ✓ |
| Fecha de recepción | `fechaRecepcion` | ✓ |
| Persona/entidad peticionaria, Correo, Dirección | `peticionario`, `correo`, `direccion` | ✓ |
| Tipo de petición + Vencimiento automático | `tipoPeticion` + computed | ✓ |
| ¿Qué están solicitando? | `queSolicita` | ✓ |
| PDF de la petición recibida | doc `peticion-recibida.pdf` (recepción) | ✓ |
| Radicado (de la respuesta) | `radicadoRespuesta` | ✓ |
| Contestación — cargar PDF | doc `respuesta.pdf` (required SI/PARCIAL) | ✓ |
| Fecha en que se contestó | `fechaContestacion` (required SI/PARCIAL) | ✓ |
| Envío: correo electrónico o físico | `medioRespuesta` | ✓ field exists, **but not required** |
| **Envío correo – Cargar PDF / Envío físico – Cargar PDF** | — | **✗ MISSING (proof of sending)** |
| ¿La petición se contestó? SI/PARCIAL/NO | `contestada` | ✓ |
| Reiteración / Recurso / Tutela | stages | ✓ |

## What changes (data-driven, no schema change)
1. **Send channel required when answering.** Add `medioRespuesta` to `camposRequeridos` of the "Respuesta"
   stage for `contestada = SI` and `contestada = PARCIAL`.
2. **Proof-of-sending document, by channel.** Offer an optional document depending on `medioRespuesta`:
   - `Correo electrónico` → `acuse-correo.pdf`
   - `Físico` → `constancia-envio.pdf`
3. **Labels.** Add `acuse-correo` → "Acuse de correo" and `constancia-envio` → "Constancia de envío" to the
   client document label map.

## Decisions
- Proof document is **optional** (offered, non-blocking) — it may not be digitized at the moment of
  recording the response; the channel itself is the required datum.
- `radicadoRespuesta` stays optional (the doc lists it without marking it mandatory).

## Out of scope
- Generable template for the Recibido (our written response) — separate follow-up.

## Rollback
Seed is idempotent; reverting restores the prior "Respuesta" stage rules. Label additions are additive.
