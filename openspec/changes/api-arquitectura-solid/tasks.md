# Tasks — Arquitectura SOLID / clean code (API)

> Backlog priorizado. NADA aplicado aún (solo auditoría). Cada ítem es independiente.
> Gate por ítem: `tsc` + `pnpm test` (465) verdes.

## 1. ALTA — single source of truth del motor (A1)
- [ ] 1.1 Decidir vehículo: paquete `@lex/procesos-core` vs. módulo compartido + test de paridad.
- [ ] 1.2 Mover `evaluarCondicion / puedeSerVerdad / campoVisible / campoEfectivamenteRequerido /
      validarDatosContraEsquema / documentos…DeEtapas` a un único origen.
- [ ] 1.3 Consumirlo desde `api/esquema.ts` y `client/lib/procesos.ts`; borrar la copia.
- [ ] 1.4 Test de paridad (mismos inputs → mismo output) como red de seguridad.

## 2. MEDIA — atajos de capa / barato y de bajo riesgo
- [ ] 2.1 (M1) `cartera.service`: mover `aggregate` a `ContableRepository`; tipar `cartera` (sin `any`).
- [ ] 2.2 (M3) Reemplazar literales `"ARCHIVADO"/"CERRADO"/"EN_PROCESO"` por `EstadoProceso.*`.
- [ ] 2.3 (M4) `config/env.ts`: fail-fast (o warn fuerte) si `isProd` y falta `DOCUMENTOS_RAIZ_PREFIJO`.

## 3. MEDIA — tipado y testabilidad
- [ ] 3.1 (M2) Helper único `etapasDe(tipo)` / `esquemaDe(tipo)`; eliminar los ~13 `as unknown as`.
- [ ] 3.2 (M5) Extraer `planificarAutoavances(proceso, etapas)` PURO; el service solo ejecuta la tx.
- [ ] 3.3 (M5) Extraer puras: `construirTituloLitigio`, `calcularTotalCobro` (totalDesdePlan),
      `calcularComision`; el service las invoca. Agregar unit tests.

## 4. BAJA — oportunista
- [ ] 4.1 (B3) `shared/dateUtils.ts` (startOfDay/endOfDay/DIA_MS); usar en comercial/ventas.
- [ ] 4.2 (B1) `categoriaDoc` + validación por tipo → tablas data-driven (si crecen los tipos).
- [ ] 4.3 (B2) Función de dominio compartida para "prospecto → cliente + proceso".
- [ ] 4.4 (B4) Helper `conflicto(entidad)` para los mensajes P2002 a medida (cosmético).

## 5. Verificación final
- [ ] 5.1 `tsc` + `pnpm test` + build de ambos frontends verdes.
- [ ] 5.2 Smokes de procesos (motor) tras tocar A1/M2/M5.
