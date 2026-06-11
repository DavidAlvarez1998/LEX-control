# Clientes · delta (convertir abogado + responsable visible, sin muro)

> Change `cliente-convert-ownership`. JURIDICO may convert; the responsable is auto-assigned to the
> creator and surfaced; there is NO ownership wall (firm-coverage standard).

## ADDED Requirements

### Requirement: No ownership wall on cliente edit/convert
The system MUST NOT block editing or converting a `Cliente` based on who its `responsableComercialId`
is. Any user of the despacho holding the relevant permiso (`cliente.editar` / `cliente.convertir`)
MAY act on ANY `Cliente` of the same `empresa`. Ownership is informational (attribution + the "Míos"
filter), NOT an authorization gate. The UI SHOULD surface the responsable (e.g. "Responsable: X") and
MAY warn when acting on another user's cliente, but MUST NOT prevent the action.

#### Scenario: A user converts another user's prospecto
- GIVEN a PROSPECTO whose `responsableComercialId` is user A, and user B holds `cliente.convertir`
- WHEN user B converts it
- THEN it succeeds (no ownership block); the UI had shown a soft notice that it belongs to A

### Requirement: Responsable comercial defaults to the creator on create
On `POST /clientes`, when the body does not set `responsableComercialId`, the system MUST set it to the
authenticated creator (`req.user.sub`). When the body sets it, that value is used (and still validated
same-empresa). This makes every prospecto have an owner for attribution and the "Míos" filter.

#### Scenario: Auto-assign creator
- GIVEN a user creates a prospecto without `responsableComercialId`
- THEN the created `Cliente` has `responsableComercialId = ` the creator's id

### Requirement: Reads expose the responsable identity
`GET /clientes` and `GET /clientes/:id` MUST include `responsableComercial { id, nombre }` (nullable)
so the UI can show who owns each cliente.

#### Scenario: List carries the responsable name
- GIVEN a cliente with a responsable
- WHEN the list is fetched
- THEN each row carries `responsableComercial: { id, nombre }`

## MODIFIED Requirements

### Requirement: RBAC — cliente.convertir includes JURIDICO
`cliente.convertir` MUST be granted to `ADMINISTRADOR`, `COMERCIAL` AND `JURIDICO` (was ADMINISTRADOR +
COMERCIAL). The abogado who does intake can activate his own prospecto without a comercial. `cliente.ver`
stays the four roles; `cliente.crear`/`cliente.editar` stay ADMINISTRADOR + COMERCIAL + JURIDICO.

#### Scenario: Abogado converts
- GIVEN a user holding only `RolEmpresa.JURIDICO` (not esAdminEmpresa)
- WHEN they POST `/clientes/:id/convertir` on a same-empresa PROSPECTO
- THEN it succeeds (200), the cliente becomes CLIENTE

### Requirement: Responsable comercial is the originator (relaxed role guidance)
The previous guidance that `responsableComercialId` SHOULD hold `RolEmpresa.COMERCIAL` is RELAXED: the
responsable is the **originator** and MAY hold `COMERCIAL` or `JURIDICO` (the abogado who brought the
client). This was never enforced in code; it remains a nullable `SetNull` FK validated same-empresa.

#### Scenario: A JURIDICO is a valid responsable
- GIVEN a prospecto created by a user holding only JURIDICO
- WHEN it is stored
- THEN `responsableComercialId` = that abogado is valid (no role rejection)
