# Litigantes Specification

## Purpose
Define the registry of litigants (`Litigante`) — the despacho's end-clients and other parties a
case involves — and how they link to trámites with a role. A litigante is reusable across many
trámites and is owned by one despacho.

## Requirements

### Requirement: Litigante registry per despacho
A `Litigante` MUST belong to one despacho (resolved from `req.user.sub`) and carry `tipoPersona`
(NATURAL | JURIDICA), `nombre`, optional `tipoDocumento` (CC | CE | NIT | TI | PASAPORTE | PEP_PPT)
with `numeroDocumento`, and optional `email`, `telefono`. The system MUST NOT use Mexican identifiers
(no `rfc`, no `curp`). Reads/writes MUST be scoped to the caller's despacho; a despacho MUST NOT see
another's litigantes. Any `USUARIO` of the despacho MAY manage its litigantes.

#### Scenario: Create litigante
- GIVEN a lawyer
- WHEN they create a litigante with `tipoPersona` NATURAL, `tipoDocumento` CC, and a `nombre`
- THEN status is 201 and it is owned by their despacho

#### Scenario: Cross-tenant isolation
- GIVEN a litigante of despacho B
- WHEN a user of despacho A lists litigantes
- THEN despacho B's litigante is NOT returned

### Requirement: Link litigantes to a trámite with a role
A `Tramite` MUST link litigantes via `ParteTramite`, each carrying a procedural `rol`
(ACTOR | DEMANDADO | TERCERO | OTRO), an optional area-specific `rolEtiqueta` (free text, e.g.
"quejoso", "trabajador", "imputado"), and `esNuestroCliente` (which side the despacho represents,
independent of procedural position). A linked litigante MUST belong to the same despacho as the
trámite. The same litigante MUST NOT be linked to the same trámite twice in the same `rol`.

#### Scenario: Link our client as actor
- GIVEN a trámite and a litigante of the same despacho
- WHEN linked with rol ACTOR and `esNuestroCliente = true`
- THEN the party appears on the trámite as our client in the actor position

#### Scenario: Reject cross-despacho litigante
- GIVEN a litigante of despacho B and a trámite of despacho A
- WHEN despacho A links it
- THEN the response status is 400

### Requirement: Reusable across trámites
A `Litigante` MUST be linkable to multiple trámites over time, and listing a litigante MUST be able
to surface its associated trámites.

#### Scenario: One litigante, many trámites
- GIVEN a litigante linked to two trámites
- WHEN the litigante is fetched
- THEN both trámites are associated
