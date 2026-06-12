# Comercial — Seguimientos (delta)

## MODIFIED Requirements

### Requirement: Typed disposition closes the contact loop
The system MUST define the additive enum `DisposicionGestion { CONTACTADO, NO_CONTESTA, INTERESADO, NO_VIABLE, OTRO }` and a nullable column `disposicion` on `seguimientos_comerciales` (additive, applied with `db push`, no backfill, no existing enum changed). The seguimiento create and update endpoints MUST accept and persist `disposicion` so the contact loop is closed with a measurable outcome (not free text only). The disposition feeds the pipeline's `ultimaDisposicion` frío/caliente signal. `NO_VIABLE` is the typed shortcut a UI uses to offer "mark fase PERDIDO" (which reuses `POST /clientes/:id/fase`, no new endpoint).

#### Scenario: Disposition persists on create
- GIVEN a user holding `comercial.seguimiento.crear`
- WHEN they POST a seguimiento with `disposicion = INTERESADO`
- THEN it is created with `disposicion = INTERESADO` and the value is returned

#### Scenario: Disposition is optional and additive
- GIVEN the pushed schema
- WHEN a seguimiento is created without `disposicion`
- THEN it is stored with `disposicion = null` AND no existing enum was modified

#### Scenario: Disposition surfaces as the pipeline signal
- GIVEN a cliente whose most recent disposed seguimiento is `INTERESADO`
- WHEN `GET /comercial/pipeline` is read
- THEN that cliente's `ultimaDisposicion = INTERESADO`
