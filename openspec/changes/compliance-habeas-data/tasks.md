# Tasks — compliance-habeas-data

> Estado: **PLAN SDD (no implementado)**. El texto legal (política/aviso/términos/DPA) requiere
> revisión de un abogado colombiano antes de publicar. Orden: schema → documentos+aceptación →
> autorización → derechos del titular → export/retención → operativo (no software).

## Fase 0 — Legal (paralelo, no es código)
- [ ] 0.1 Abogado redacta/aprueba: Política de Tratamiento, Aviso de Privacidad, Términos, DPA (encargo despacho↔plataforma)
- [ ] 0.2 Registrar las bases de datos en el **RNBD** de la SIC
- [ ] 0.3 Designar responsable/oficial de protección de datos + correo de contacto (habeasdata@…)

## Fase 1 — Schema (`lex-control-api`)
- [ ] 1.1 Modelos `DocumentoLegal`, `AceptacionLegal`, `AutorizacionTratamiento`, `SolicitudTitular` + enums (tipo, canal, estado, titularTipo)
- [ ] 1.2 Campos opcionales de consentimiento en `Cliente` y `Litigante` (`autorizacionTratamiento`, `autorizacionFecha`, `autorizacionCanal`)
- [ ] 1.3 `pnpm push` (DB no gestionada por migrate) + `pnpm generate`
- [ ] 1.4 Seed: insertar versión 1 (placeholder) de cada `DocumentoLegal`

## Fase 2 — Documentos legales + aceptación
- [ ] 2.1 Módulo `cumplimiento` (router→service→repository→dto): `GET /publico/legal/:tipo` y `/:tipo/:version`; `POST/PATCH /legal/documentos` (ADMIN; published = inmutable → 409)
- [ ] 2.2 Gate de aceptación: registrar `AceptacionLegal` en set-password; `GET /auth/me` y login devuelven `aceptacionPendiente`
- [ ] 2.3 Frontends: páginas públicas legales + enlaces en footer (ambos portales / marketing)
- [ ] 2.4 Activación: checkbox requerido (`*` rojo, validar en submit) "Acepto Términos y Política"
- [ ] 2.5 Modal bloqueante de re-aceptación cuando hay versión nueva `requiereReaceptacion`
- [ ] 2.6 Tests: serve público, inmutabilidad (409), 403 no-admin, gate de aceptación + re-aceptación

## Fase 3 — Autorización de tratamiento
- [ ] 3.1 Endpoints de `AutorizacionTratamiento` (crear/revocar) scoped por tenant; platform-level para USUARIO/PROSPECTO
- [ ] 3.2 Captura inline en formularios de `Cliente`/`Litigante` (¿autorizó?/canal/fecha) + reflejo en campos de conveniencia
- [ ] 3.3 Datos sensibles: exigir consentimiento explícito + `finalidades` no vacías (400 si falta)
- [ ] 3.4 Subida de evidencia (autorización en papel escaneada) vía `documental-storage`
- [ ] 3.5 Tests: captura por despacho, datos sensibles, revocación conserva histórico

## Fase 4 — Derechos del titular (PQR Habeas Data)
- [ ] 4.1 `SolicitudTitular` CRUD + bandeja por Responsable (tenant vs plataforma); `POST /publico/legal/solicitud` (rate-limited)
- [ ] 4.2 `fechaLimite` por tipo (consulta 10 / reclamo 15 días hábiles, motor `diasHabiles`) + `GET /cumplimiento/solicitudes/vencimientos` con semáforo
- [ ] 4.3 UI: sección "Datos personales / Habeas Data" (cliente: las suyas; admin plataforma: las de la plataforma) con responder/resolver
- [ ] 4.4 Tests: deadlines, ruteo por tenant, vencimientos, intake público

## Fase 5 — Retención, export y supresión
- [ ] 5.1 `GET /mi-empresa/exportar-datos` (export scoped por `empresaId`)
- [ ] 5.2 Flujo de `SUPRESION`: borra salvo deber legal de retención (responde con la base legal); log de la acción
- [ ] 5.3 Documentar política de retención + medidas de seguridad (TLS/cifrado dependen del deploy → [[api-camino-a-perfecta]])

## Cierre
- [ ] Gate: tsc + tests + builds verdes; smoke en vivo (serve legal, aceptación, una solicitud con deadline)
- [ ] Fusionar spec delta a `openspec/specs/compliance-habeas-data/` y archivar el change
- [ ] Actualizar memoria
