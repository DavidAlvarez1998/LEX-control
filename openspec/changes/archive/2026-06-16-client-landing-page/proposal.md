# client-landing-page

## Por qué

Hoy el portal cliente (`lex-control-client`) abre directo en el login: la raíz `/`
es el home del dashboard (protegido) y un visitante sin sesión solo ve el formulario
de ingreso. LEX Control necesita una **página web pública** que presente el producto
a los despachos (propuesta de valor, módulos, cómo funciona, planes) y desde ahí
conduzca al login o a solicitar una demo. Esta landing pasa a ser la cara pública
del producto; el login deja de ser la primera pantalla.

## Qué cambia

### Frontend (lex-control-client) — capability `public-landing`
- **Routing**: la landing pública vive en `/` (sin sidebar, sin auth). El home del
  dashboard se mueve de `/` → `/inicio`. El resto de rutas (`/procesos`, `/clientes`,
  `/contable`, …) NO cambia. Login (`/login`) y activación (`/activar`) se mantienen.
- **Redirecciones**: login y "ir al portal" apuntan a `/inicio`; el ítem "Inicio" del
  sidebar repunta a `/inicio`; el guard de sesión del dashboard redirige a `/login`.
  Un usuario YA autenticado que entre a `/` ve un CTA "Ir a mi portal" → `/inicio`.
- **Secciones** (tono *SaaS legal moderno*: índigo de marca, Geist, claro/oscuro):
  1. **Header** público (logo LEX Control + botón "Ingresar").
  2. **Hero** + 2 CTAs: "Ingresar" (→ `/login`) y "Solicitar demo" (→ form).
  3. **Módulos / Funcionalidades**: tarjetas (Procesos & Derecho de Petición, CRM
     Comercial, Contable, Contratos, Facturación, Agenda, Consulta judicial).
  4. **Cómo funciona / Beneficios**: 3-4 beneficios clave (deadline-first, multi-rol
     por despacho, todo en un lugar, datos del juzgado al día).
  5. **Planes / Precios**: tarjetas traídas de la API pública de planes.
  6. **CTA final + Footer**.
- **Solicitar demo**: formulario (despacho, contacto, email, teléfono, mensaje) que
  capta el lead en el embudo comercial de la plataforma.

### Backend (lex-control-api) — capability `public-marketing-api`
- **`GET /publico/planes`** — SIN auth. Proyección mínima de planes `activo=true`
  ordenados por `orden`: `{ clave, nombre, descripcion, precioMensual, modulos[], cuotas[] }`.
  No expone IDs internos de suscripción ni datos sensibles.
- **`POST /publico/solicitud-cuenta`** — SIN auth. MODELO HÍBRIDO (pendiente de
  aprobación): crea un `Prospecto` (`canalEntrada = WEB`, `estado = NUEVO`) con los
  datos del despacho (nombre/NIT/correo/teléfono) + del usuario admin (nombre/correo/
  teléfono) + plan elegido (`planClave → planInteresId`). NO da acceso: el equipo lo
  aprueba (GANADO) y el flujo de ventas existente provisiona Empresa + admin +
  suscripción. Anti-spam: honeypot + zod. El correo/teléfono de empresa van a `notas`.

## Impacto
- Schema: **sin cambios** (reusa Plan/Prospecto existentes).
- Backend: +2 endpoints públicos (nuevo router `/publico`), montados antes del 404.
- Frontend: +1 ruta pública (`/`), home dashboard movido a `/inicio`, +componentes de
  landing. Toca `nav.tsx`, `login`, y el guard del dashboard (repunte de `/`→`/inicio`).
- Seguridad: 2 endpoints públicos de solo-lectura/captación; `solicitar-demo` es write
  público → honeypot + validación estricta + sin exponer errores internos.

## Fuera de alcance (v1)
- CMS / contenido editable (textos hardcodeados salvo planes).
- SEO avanzado, blog, multi-idioma, analítica.
- Captcha de terceros (se deja honeypot; se puede subir a reCAPTCHA luego).
- Landing del portal admin (esto es solo el frontend cliente).

## Decisiones del usuario (2026-06-16)
- Tono: **SaaS legal moderno** (marca índigo actual).
- Secciones: Hero+CTA, Módulos, Cómo funciona, **Planes** (desde API).
- Planes: **desde la API** (nuevo endpoint público de solo lectura).
- CTA: **Ingresar + Solicitar demo**.
