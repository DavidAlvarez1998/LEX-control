# Tasks — contable-nomina-desde-contrato

## Schema
- [x] Ninguno — Nómina ya tiene `empleadoId`/`fechaIngreso` y todos los campos; Contrato ya existe.

## API (módulo contable)
- [x] `GET /contable/nominas/empleables` — proyección mínima `{contratoId, usuarioId, nombre, cargo, honorarios, tipoContrato, fechaInicio, estado}` de `Contrato` `WHERE { empresaId }` (token)
- [x] Gate `requireAuth` + `requirePermiso('contable.nomina.crear')` + módulo `contable`; NO concede `contrato.ver`; NO expone campos legales/documentos (select acotado)
- [x] Devuelve todos los estados + `estado` en la proyección (filtro de vigentes/liquidación lo hace la UI)
- [x] `assertEmpleado(empresaId, empleadoId)` + validación en POST/PATCH `/nominas` (cierra requisito de spec antes sin implementar)
- [x] helper de mapeo `tipoContrato (texto) → TipoVinculacion (enum)` con fallback `OTRO` (lado cliente)
- [x] tests: empleables proyección/scoping/sin-cláusulas; empleadoId otra empresa→400; mismo despacho→201

## Frontend (cliente — nomina.tsx + lib/contable.ts)
- [x] tipo `Empleable` + `contableApi.empleables()`
- [x] cargar `empleables` al montar; selector "Colaborador (contrato)" que prellena nombre/cargo/vinculación/salario + antigüedad
- [x] "Empleado" sigue siendo Input libre (fallback); opción "Otro — sin contrato (excepción)" con aviso ámbar
- [x] check "incluir finalizados/suspendidos (liquidación)" (default solo ACTIVO)
- [x] NO prellenar bonificaciones/descuentos/cuenta; enviar `empleadoId`/`fechaIngreso` en el payload

## Verify
- [x] `pnpm --dir lex-control-api build` (tsc) limpio
- [x] `pnpm --dir lex-control-client build` (next) limpio
- [x] `pnpm --dir lex-control-api test` → 373/373 (3 nuevos)
- [x] smoke en vivo (BD real) 4/4: empleables 200 (proyección mínima, sin cláusulas, con estado) · POST empleadoId válido 201 (guarda empleadoId) · POST empleadoId de otra empresa 400 · snapshot intacto (cambié honorarios contrato 2M→9.999.999, nómina siguió 2M). Limpieza: nómina de prueba borrada + contrato restaurado
