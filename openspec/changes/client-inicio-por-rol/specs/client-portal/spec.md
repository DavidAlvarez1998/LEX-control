# Client Portal Specification — delta (client-inicio-por-rol)

## ADDED Requirements

### Requirement: Role-aware home dashboard
The client portal home (`/inicio`) MUST present only the KPIs, alerts and quick-access cards
of the sections the user can access, using the same visibility predicate as the sidebar
(`adminOnly` → esAdminEmpresa; `roles` → esAdminEmpresa or the user has one of the roles; no
mark → everyone). It MUST fetch only the data for sections the user can see (no requests that
would 403). Every KPI card MUST navigate to its section.

#### Scenario: JURIDICO sees processes, not accounting
- GIVEN a user whose only empresa role is JURIDICO
- WHEN they open `/inicio`
- THEN they see the Procesos KPI (linking to `/procesos`) and the vencimientos card
- AND they do NOT see the "Cartera pendiente" / "Utilidad del mes" accounting KPIs
- AND no request is made to the accounting endpoints

#### Scenario: CONTABLE sees accounting, not the commercial pipeline
- GIVEN a user whose only empresa role is CONTABLE
- WHEN they open `/inicio`
- THEN they see the Cartera and Utilidad KPIs (linking to `/contable`)
- AND they do NOT see the commercial "Pendientes" (alertas) card

#### Scenario: KPI cards navigate
- GIVEN any KPI card on `/inicio`
- WHEN the user clicks it
- THEN they navigate to that KPI's section (e.g. Procesos → `/procesos`, Cartera → `/contable`)

#### Scenario: Empresa admin sees everything
- GIVEN a user with esAdminEmpresa
- WHEN they open `/inicio`
- THEN they see the union of all role widgets
