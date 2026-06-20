# convencion-integraciones-externas

## Por qué

Vamos a incorporar **varias APIs externas** (terceros: gobierno, validación de NIT, pasarelas de
pago, etc.) al sistema. Antes de implementar ninguna, fijamos **una convención canónica** de cómo se
integra un tercero en LEX Control: cómo se **crea** en la API, cómo se **expone** a los portales y
cómo se **consume** en el front. Así toda integración futura se ve igual, es predecible, y cambiar de
proveedor o de entorno cuesta tocar `env`, no los módulos.

Es el mismo espíritu transversal que [[documental-storage]] (estándar de subida de archivos): este
documento es el estándar para **consumir servicios HTTP de terceros**. Referencia de implementación
viva: `lex-control-api/src/modules/documentos/documentos.client.ts` (tecnovapp). El módulo que
borramos (`integraciones-estatales`) seguía esta forma; lo que faltó fue dataset/proveedor real y
validación, no la arquitectura.

> Alcance de este change: **solo la convención (pautas)**. No implementa ninguna API concreta. Cada
> API real se hará luego como su propio change que **referencia** y **cumple** esta spec.

## Las 3 fases de toda integración (mapa mental)

```
   CREAR (en la API)            EXPONER (a los portales)        CONSUMIR (en el front)
   ──────────────────           ────────────────────────        ──────────────────────
   client.ts  ── fetch ─►🌐      router.ts  ── /ruta ──┐          lib/<x>-api.ts  (api.get)
   service.ts (negocio)         requireAuth+Permiso   │              │
   types.ts   (DTO propio)      valida zod, tenant    │              ▼
   schemas.ts (validación)                            └──► JSON  componente.tsx
   env.ts     (URL+llave)
```

## Estructura y naming de un módulo de integración

Todo tercero nuevo vive en `lex-control-api/src/modules/<nombre>/` con estos archivos:

| Archivo | Rol | Regla |
|---|---|---|
| `<nombre>.client.ts` | 🌐 Habla con el tercero | **ÚNICO** archivo con `fetch` afuera; normaliza a DTO propio |
| `<nombre>.service.ts` | 🧠 Negocio | Orquesta, cachea, persiste, valida tenant; nunca hace `fetch` |
| `<nombre>.router.ts` | 🚪 Endpoint HTTP | `requireAuth` + `requirePermiso`; tenant del token |
| `<nombre>.schemas.ts` | ✅ Validación zod | Entrada (params/body/query) y, si aplica, salida |
| `<nombre>.types.ts` | 📐 DTOs | La forma normalizada que ve el negocio (independiente del tercero) |
| `<nombre>.repository.ts` | 🗄️ BD (opcional) | Solo si se persisten datos del tercero; tenant-scoped |

Conexión y secretos: bloque `env.<nombre>` en `src/config/env.ts` (← `.env`). Montaje: 1 import +
`app.use("/<ruta>", <nombre>Routes)` en `src/app.ts`.

## Consumo en el front

El navegador **nunca** llama al tercero: llama a NUESTRO endpoint vía `src/lib/<nombre>-api.ts`
usando el helper `api` (`api.get/post/...` de `lib/api.ts`), que ya da token JWT, manejo de 401,
timeout y parseo de errores. Las requests salen por el proxy same-origin `/api` (`next.config.ts`).

## Qué NO cambia

No se crea ninguna ruta ni modelo en este change. Solo queda la spec canónica
`integraciones-externas` para que las integraciones reales la sigan.
