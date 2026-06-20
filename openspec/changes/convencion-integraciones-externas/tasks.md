# Tasks — convencion-integraciones-externas

## Documentación (este change)
- [x] Proposal con el mapa de las 3 fases (crear / exponer / consumir) + tabla de archivos y naming
- [x] Spec canónica `integraciones-externas` con las pautas como Requirements + Scenarios
- [ ] Revisión del usuario y archivado (specs → `openspec/specs/integraciones-externas/`)

## Pendiente para CADA API real (no en este change)
- [ ] Crear el change propio que referencia esta convención
- [ ] Decidir proveedor, endpoints expuestos, env vars y (si aplica) modelos Prisma
- [ ] Implementar capas `<nombre>.{client,service,router,schemas,types}.ts` (+ `repository` si persiste)
- [ ] `lib/<nombre>-api.ts` + consumo en componente(s)
- [ ] Gate: `tsc` + tests + build; smoke contra el proveedor real

## Opcional (próximo paso si se aprueba)
- [ ] Generar un MÓDULO PLANTILLA esqueleto (client/service/router/schemas/types + lib front) listo
      para copiar por cada integración nueva
