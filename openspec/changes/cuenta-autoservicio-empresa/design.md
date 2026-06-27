# Diseño — cuenta-autoservicio-empresa

## Flujo (POST /publico/solicitud-cuenta)

```
visitante → form "Crea tu cuenta" → POST /publico/solicitud-cuenta
  ├─ honeypot `website` no vacío  → 200 no-op (bot ve éxito), no crea nada
  ├─ email ya existe (Usuario)    → 409 "Ya existe una cuenta con ese correo"
  ├─ NIT ya existe (Empresa.rfc)  → 409 "Ya existe una empresa con ese NIT/CC"
  └─ válido →
      tx {
        empresa  = Empresa.create { nombre, rfc, email, activo:true }
        plan     = resolverPlanTrial()                 // env PLAN_AUTOSERVICIO_CLAVE
        if plan: Suscripcion.create { empresaId, planId, estado:ACTIVA }
        token    = generateActivationToken()           // { raw, hash }
        usuario  = Usuario.create {                      // estado PENDIENTE (no fija activo)
                     email, nombre, telefono, tarjetaProfesional,
                     rol:USUARIO, empresaId, esAdminEmpresa:true,
                     password: placeholder, activationToken: hash,
                     activationExpires: now+48h }         // activo default true → PENDIENTE
        UsuarioRolEmpresa.create { usuarioId, rolEmpresa:ADMINISTRADOR, empresaId }
        Prospecto.create {
                     nombreEmpresa, nombreContacto, email, telefono,
                     numeroDocumento:rfc, canalEntrada:WEB, estado:GANADO,
                     empresaId, planVendidoId: plan?.id, fechaCierre: now,
                     comercialId:null, notas:"Alta autoservicio web" }
      }
      // best-effort, fuera de la tx:
      correoEnviado = enviarInvitacionCuenta({ to:email, nombre,
                        activationUrl: clientUrl/activar?token=raw, contexto:"empresa" })
      → 201 { ok:true }
```

El usuario nace en estado **PENDIENTE** (mismo patrón que el alta de usuarios del admin): `activo`
queda en su default `true`, pero con `password` placeholder (no bcrypt → no autentica) + token de
activación. `deriveEstado` lo reporta PENDIENTE y no puede iniciar sesión hasta poner contraseña.
(No se fija `activo:false`: eso sería INACTIVO/deshabilitado, otro estado.)

Activación: el abogado abre el link → portal cliente `/activar?token=…` → `setPassword` (existente)
pone bcrypt, `activo:true`, limpia token, `tokenVersion++`. Ya puede entrar como ADMINISTRADOR de
su empresa.

## Por qué NO reusar `usuarios.createUsuario`

`createUsuario` está pensado para el **admin** creando usuarios dentro de una empresa **ya existente**:
valida cupos/asientos del plan (`RolEmpresa`), exige contexto autenticado y devuelve `activationUrl`
para la UI admin. En el alta autoservicio creamos **empresa + suscripción + usuario + prospecto** en
**una sola transacción** y sin sesión. Por eso `publico.service` orquesta directo con el repo y reusa
solo las **piezas** compartidas (token, `activationUrl`, `enviarInvitacionCuenta`), no el orquestador
admin. La lógica de token/correo NO se duplica: se importa de `auth.service`/`notificaciones`.

## Por qué NO reusar `ventas.ganarProspecto`

`ganarProspecto` parte de un Prospecto existente y crea Empresa + Suscripción + **Comisión** para el
comercial dueño. Aquí el orden está invertido (empresa primero) y **no hay comercial** → no hay
comisión. Creamos el Prospecto `GANADO` ya ligado a la empresa, directamente, sin pasar por ese
orquestador. `Prospecto.empresaId` es `@unique` → 1 prospecto por empresa (consistente).

## Plan trial por defecto

- Config: `env.PLAN_AUTOSERVICIO_CLAVE` (ej. `"trial"`). `resolverPlanTrial()` busca el Plan activo
  por esa clave.
- **Cupos**: el plan trial DEBE tener al menos 1 asiento `ADMINISTRADOR` (cuota) para que el primer
  usuario quepa. El seed de planes debe garantizarlo. Como en el alta creamos el primer y único
  ADMINISTRADOR, no validamos cupo contra el plan en este flujo (la empresa recién nace); el control
  de cupos sigue operando para altas posteriores vía el flujo admin normal.
- **Alcance del trial (decisión 2026-06-27):** el plan trial da acceso **completo** — TODOS los
  módulos no-baseline (contable, comercial, contratos, ia_redaccion, logo_personalizado,
  automatizacion_contratos) y cupos **ilimitados** (`limite = null`) en los 4 roles
  (ADMINISTRADOR, JURIDICO, CONTABLE, COMERCIAL). Antes era baseline-only + 1 ADMINISTRADOR + 1
  JURIDICO; se abrió para que el usuario pruebe la plataforma entera sin topar con el muro "Módulo
  no contratado". Sembrado en `src/seed-foundations.ts` (array `PLANES`). Trade-off conocido: toda
  alta gratuita recibe todo ilimitado; revisar antes de monetizar el free tier.
- **Degradación**: si la clave no resuelve, se crea la empresa **sin** suscripción y se loggea
  `[publico] plan autoservicio no encontrado`. El alta NO se bloquea (el usuario igual activa y entra;
  un admin puede asignar plan luego). Se prefiere alta-con-aviso sobre alta-fallida.

## Cambio de schema (único)

```prisma
model Usuario {
  // …
  telefono String?   // teléfono de notificación personal (alta autoservicio + perfil)
}
```

Aditivo y nullable. Se aplica con `pnpm push` (la DB de dev NO usa `prisma migrate` — `migrate`
resetea datos). `pnpm generate` después para el cliente tipado. Todo lo demás ya existe en el
schema (`Empresa.rfc @unique`, `Empresa.email`, `Usuario.tarjetaProfesional`, `Prospecto` con
`estado GANADO`/`empresaId @unique`/`canalEntrada WEB`, `Suscripcion`, `UsuarioRolEmpresa`).

## Validación (zod) del body

```
nombreEmpresa  string  req  (1..160)   → Empresa.nombre
nit            string  req  (1..40)    → Empresa.rfc
tarjeta        string  opt  (..60)     → Usuario.tarjetaProfesional
email          string  req  email      → Usuario.email + Empresa.email
telefono       string  req  (5..30)    → Usuario.telefono
nombreContacto string  req  (1..120)   → Usuario.nombre
website        string  opt             → honeypot (no-op si viene)
```
El cliente NO puede inyectar `estado`, `empresaId`, `rol`, `activo`, `planId`: no están en el schema
de entrada. El plan se decide server-side (trial), no por el cliente.

## Anti-abuso (resumen)

| Vector                    | Mitigación                                                        |
|---------------------------|-------------------------------------------------------------------|
| Bots/spam                 | honeypot `website` + rate-limit `/publico` (30/h) ya existentes   |
| Cuenta usable sin validar | `activo:false` hasta activar por correo (token 48 h)              |
| Email/NIT duplicado       | `Usuario.email @unique` + `Empresa.rfc @unique` → 409 explícito   |
| Empresa basura            | admin puede `Empresa.activo=false` (bloquea login, ya existe)     |

## Idempotencia / errores

- Toda la creación va en **una transacción**: si algo falla, no quedan empresas huérfanas.
- El **correo** va fuera de la tx (best-effort): si falla, la cuenta existe y el admin reenvía con
  `resetPassword`. Se devuelve 201 igual (no se filtra el fallo de correo al visitante).
- Respuestas de error públicas: genéricas, sin stack ni internals.
