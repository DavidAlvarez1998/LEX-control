# Proceso Vencimientos Specification — delta (client-procesos-vista-todos)

## ADDED Requirements

### Requirement: Process list supports deadline-first ordering
The process list endpoint (`GET /procesos`) MUST accept an optional `orden=vencimiento` query
parameter. When present, results MUST be ordered server-side so that open processes sort by
`fechaLimite` ascending with null deadlines last, and closed/archived processes sort after all open
ones. This makes overdue → due-soon → on-time → no-deadline → closed the natural page order, so
pagination preserves the deadline-first ordering. When the parameter is absent, the endpoint MUST
behave exactly as before (additive, backward-compatible). The `semaforo` value per item is unchanged.

#### Scenario: Deadline-first ordering with nulls last
- GIVEN open processes with deadlines and some without
- WHEN `GET /procesos?orden=vencimiento` is requested
- THEN processes with the earliest `fechaLimite` come first and processes without a deadline come
  after all dated open processes

#### Scenario: Closed processes ordered last
- GIVEN open and CERRADO/ARCHIVADO processes
- WHEN `GET /procesos?orden=vencimiento` is requested
- THEN every closed/archived process sorts after all open processes

#### Scenario: Absent parameter is backward-compatible
- GIVEN a client that does not send `orden`
- WHEN `GET /procesos` is requested
- THEN the ordering is identical to the prior behavior
