# Clientes & Prospectos (delta)

## MODIFIED Requirements

### Requirement: The CRM list surfaces derived seguimiento signals
The clientes list MUST be readable as a pipeline at a glance: the derived seguimiento signals (`ultimaGestionEn`/`diasSinGestion`, `proximaTareaEn`/`tareaVencida`, `faseActual`/`diasEnFase`, `ultimaDisposicion`) are supplied by `GET /comercial/pipeline` (see capability `comercial-pipeline`) and consumed by the CRM list with quick filters (`?mios`, frío, vencidas, fase). These signals MUST remain computed on read and MUST NOT add stored columns to `Cliente`.

#### Scenario: List shows signals without new stored fields
- GIVEN the CRM list of a despacho
- WHEN it renders a cliente row
- THEN it shows the cliente's derived signals sourced from the pipeline endpoint AND no signal is persisted on the `Cliente` row
