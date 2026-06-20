# Integraciones Estatales (delta: REMOVED)

Esta capacidad se retira por completo del proyecto: nunca se conectó ni validó (dataset placeholder,
proveedores bloqueados por infra/llaves, bloque oculto en UI). Todos sus requisitos quedan eliminados
y la spec canónica se borra.

## REMOVED Requirements

### Requirement: Normalized provider adapter
**Reason:** No hay adapters reales en uso; el módulo `src/modules/integraciones/` se elimina.

### Requirement: Sync actuaciones by radicado, idempotently
**Reason:** El motor de sincronización y los modelos `ActuacionJudicial`/`IntegrationSyncLog` se
eliminan; nunca corrió contra un proveedor real (solo mock en dev).

### Requirement: Sync triggers and rate protection
**Reason:** Sin proveedores ni cola de scraping; se elimina junto con el módulo.

### Requirement: Per-despacho provider configuration and credentials
**Reason:** El modelo `ProviderConfig` y el cifrado de credenciales se eliminan (sin proveedores que
configurar).

### Requirement: Tenant scoping of synced data
**Reason:** No quedan datos sincronizados (las 3 tablas se eliminan).

### Requirement: Compliance with habeas data
**Reason:** No se ingiere ningún dato personal desde sistemas estatales; el cumplimiento de habeas
data sigue cubierto para el resto del dominio por [[compliance-habeas-data]].
