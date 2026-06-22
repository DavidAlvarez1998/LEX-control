# design — rama-judicial-actuaciones (encaje + decisiones abiertas)

## Cómo encaja en nuestro modelo (verificado en `schema.prisma`)

- **Entrada lista:** `Proceso.radicado String?` (línea ~395, comentario "23 dígitos del juzgado;
  nulo hasta radicar") con `@@index([radicado])`. Es exactamente lo que pide el Endpoint A.
  En el ejecutivo de mínima cuantía el radicado se captura (campos `nroRadicado` /
  `fechaRadicacion` en el seed) → al poblar `Proceso.radicado` ya podríamos consultar.
- **`Proceso.despachoJuzgado`, `proximaAudiencia`** existen → la respuesta de la API (despacho,
  fechaUltimaActuacion) podría validar/enriquecer estos campos.
- **NO existe modelo de actuaciones.** El `historial` actual es `EtapaProceso[]` = avance de
  nuestras **etapas internas** del motor; las actuaciones de la Rama son un **flujo externo
  distinto** (lo que publica el juzgado). No se deben mezclar: hace falta un modelo nuevo.

## Mapeo de campos (API → posible modelo)

| API (actuación) | Tipo | Uso propuesto |
|---|---|---|
| `fechaActuacion` | DateTime | fecha del movimiento (orden + "nuevas desde") |
| `actuacion` | String | título del movimiento |
| `anotacion` | String? | detalle |
| `fechaInicial` / `fechaFinal` | DateTime? | términos asociados (suelen venir null) |
| `fechaRegistro` | DateTime? | cuándo lo registró la Rama |
| (de Endpoint A) `idProceso` | Int/BigInt | cachear en `Proceso` para no re-consultar A cada vez |
| (de Endpoint A) `fechaUltimaActuacion` | DateTime | **atajo**: si no cambió, saltar Endpoint B |

**Anti-duplicado:** la API no da un id por actuación → la clave natural candidata es
`(procesoId, fechaActuacion, actuacion, anotacion)` o un hash de esos campos. A confirmar en fase 2.

## Restricciones técnicas a resolver antes de implementar

1. **Puerto 448 + HTTPS saliente** desde nuestra API hacia internet (en SERVICIUDAD corre en
   `10.10.10.126`). Hay que confirmar que el server de lex-control-api **puede salir** a
   `consultaprocesos.ramajudicial.gov.co:448` (firewall/egress). Probar con el cURL del spec.
2. **User-Agent de navegador obligatorio** (sin él → 403). Nuestro transporte `fetch` debe fijarlo.
3. **Rate-limiting:** respetar los delays del §4 del spec. Para on-demand (1 proceso) es trivial;
   para CRON masivo hay que implementar el batching + backoff.
4. **`axios` del módulo fuente → `fetch`** para seguir [[convencion-integraciones-externas]]
   (client.ts único, fetch→DTO, sin dependencia nueva). El módulo fuente es solo referencia.

## Decisiones abiertas (para el usuario — definen la fase 2)

1. **¿Cuándo se actualiza?**
   - (a) **On-demand**: botón "Actualizar actuaciones" en la ficha del proceso (1 request del usuario).
   - (b) **CRON nocturno** que recorre todos los procesos con radicado (como SERVICIUDAD).
   - (c) **Ambos**: on-demand + CRON. (Recomendado a futuro; empezar por on-demand es más simple y
     prueba la conectividad sin exponernos al rate-limit masivo.)
2. **Alcance de procesos:** ¿solo mínima cuantía al inicio, o cualquier `Proceso` con radicado?
3. **Persistencia:** ¿guardamos las actuaciones (modelo `ActuacionProceso`) o solo se muestran en
   vivo? Guardarlas permite "marcar nuevas" y notificar; mostrar en vivo es más simple pero re-consulta.
4. **Notificación de novedades:** ¿avisar (in-app / correo, reusando [[correos-cuenta-invitacion-reset]]
   / notificaciones) cuando aparezca una actuación nueva? Encaja con el spine Cliente+Proceso.
5. **idProceso:** ¿lo cacheamos en `Proceso` (campo nuevo) para saltar el Endpoint A en cada sync?

## Siguiente paso

Confirmar las 5 decisiones de arriba. Con eso se redacta `tasks.md` de la fase 2 (migración del
modelo, `rama-judicial.client.ts` con fetch+DTO+anti-bloqueo, servicio de sync idempotente, endpoint
propio, UI en la ficha, y smoke real contra un radicado de prueba como `66001333300320140049500`).
