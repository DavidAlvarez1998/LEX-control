# rama-judicial-actuaciones

## Por qué

Traer automáticamente las **actuaciones** (movimientos/actualizaciones) que el juzgado
publica de un proceso, consultando la **API pública oficial de la Rama Judicial de Colombia**
(Consulta de Procesos Nacional Unificada, CPNU) a partir del **radicado de 23 dígitos**.

Arrancamos en el **proceso ejecutivo de mínima cuantía** (civil) — ver
[[proceso-ejecutivo-minima-cuantia]] — porque es judicial, lleva radicado y se beneficia de ver
el expediente al día sin entrar al portal de la Rama. La integración se diseña **reutilizable**
para cualquier `Proceso` con `radicado` (laboral, verbal, etc.), pero el alcance inicial es solo
mínima cuantía.

Fuente: `openspec/roadmap-docs/APIs/api_actuacciones.odt` — **API validada en vivo** desde el
proyecto SERVICIUDAD (servidor `serviciudad`, `judicialBranch.services.ts`): conexión, consulta
y paginación funcionando contra radicados reales.

> Relación con la limpieza de [[remove-integraciones-estatales]] (2026-06-20): aquella eliminó una
> integración estatal **nunca conectada ni validada** (jurisprudencia Corte Const. SODA + un motor
> de sync de actuaciones sin probar). Esto **NO** la contradice: es una implementación **distinta y
> ya probada en producción** de SOLO la pieza de actuaciones por radicado (CPNU), que reintroducimos
> con base sólida y alcance acotado.

## Alcance de ESTE change (fase 1: ENTENDER)

Lo que el usuario pidió primero: **identificar cómo funciona la API — qué pide y qué retorna**.
Por eso este change entrega, por ahora, el **estudio del contrato** (no código):

- `specs/rama-judicial/spec.md` — contrato canónico: endpoints, request, response, errores,
  paginación, headers obligatorios y estrategia anti-bloqueo (rate limiting + retry).
- `design.md` — cómo encaja en nuestro modelo (`Proceso.radicado` como entrada; falta un modelo
  para guardar actuaciones) y las **decisiones abiertas** a confirmar con el usuario antes de implementar.

## Lo que NO se decide aún (fase 2: requiere decisión del usuario)

- **Disparo**: CRON nocturno (como SERVICIUDAD) vs. on-demand (botón "Actualizar") vs. ambos.
- **Persistencia**: nuevo modelo `ActuacionProceso` (qué campos, índice anti-duplicado).
- **UI**: dónde se ven las actuaciones en la ficha del proceso y cómo se marca "nuevas".
- **Transporte**: adaptar al patrón del repo (`fetch` + http único + DTO, como
  [[convencion-integraciones-externas]]) en vez de `axios` del módulo fuente.
- **Conectividad/HTTPS** desde nuestra API hacia el puerto **448** (no 443) y el User-Agent obligatorio.

Una vez confirmadas esas decisiones, la fase 2 (modelo + cliente + sync + UI + pruebas) se planifica
en su propio bloque de tasks.
