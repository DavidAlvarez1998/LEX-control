# cuenta-y-contratos-tarjeta-profesional

## Por qué

Tres pedidos del usuario sobre el portal cliente (:3001), todos girando alrededor
de la **tarjeta profesional** del abogado (y la cédula), que ya existen en
`Usuario` (`Usuario.cedula`, `Usuario.tarjetaProfesional`) y ya se usan en las
plantillas de documentos como `proceso.responsable.{cedula,tarjetaProfesional}`
(poderes, demandas, terminaciones — "T.P. No. … C.S.J."). Hoy esos campos solo
se pueden fijar **al crear** el usuario (equipo/admin); el propio usuario no
puede verlos ni editarlos, y no se ven en contratos.

1. **Mi cuenta es de solo lectura.** `/cuenta` muestra perfil + empresa + "Mi
   contrato", pero el usuario **no puede editar nada** suyo — ni su tarjeta
   profesional ni su cédula ni su teléfono. Un abogado nuevo (alta autoservicio o
   creado sin esos datos) no tiene forma de completarlos, y sin ellos los
   documentos generados salen con la firma incompleta.

2. **Contratos no muestra a todo el equipo.** En la vista de admin de empresa,
   la **lista de contratos** solo enseña a quien *ya tiene un contrato creado*.
   Un miembro sin contrato (p. ej. David Alvarez, JURIDICO de Bufete Goodman) no
   aparece. NO es un bug de filtrado: `/mi-empresa/usuarios` devuelve a todo el
   equipo y el desplegable "Vincular usuario" sí lo incluye; simplemente la
   *lista* es de contratos, no de personas. Falta visibilidad de "quién del
   equipo aún no tiene contrato".

3. **Contratos no muestra la tarjeta profesional.** La pestaña "Datos" del
   contrato no muestra la tarjeta profesional (ni la cédula) del usuario
   vinculado. El contrato tampoco la trae del API (no incluye al `usuario`).

## Qué cambia

### A. Mi cuenta — editar el perfil profesional propio
Agregar en `/cuenta` una tarjeta **"Datos del profesional"** editable por el
propio usuario, con: **cédula**, **tarjeta profesional**, **teléfono**. (nombre y
correo siguen siendo de identidad/login → los gestiona el admin de empresa).
- Backend: `GET /mi-empresa/perfil` (datos propios) + `PATCH /mi-empresa/perfil`
  (autoservicio, sin requireEmpresaAdmin — cualquier USUARIO edita lo SUYO).
  Reusa el patrón tenant (userId del token; nunca toca a otro).
- Alternativa considerada: extender `GET/PATCH /auth/me`. Se prefiere
  `/mi-empresa/perfil` para no inflar el contrato de auth (sesión/roles).

### B. Contratos — ver a todo el equipo  → DESCARTADO
El usuario decidió **dejar la lista de contratos como está** (solo contratos
creados). El desplegable "Vincular usuario" ya incluye a todo el equipo (incluido
David Alvarez); para que alguien aparezca en la lista se le crea su contrato.
Sin cambios.

### C. Contratos — tarjeta profesional en "Datos"  → campo propio del contrato
- Modelo: agregar `Contrato.tarjetaProfesional String?` (decisión del usuario:
  campo propio, editable, permite override y personal externo sin cuenta).
  Sin migrate → `pnpm push` (campo nullable, aditivo).
- Backend: aceptar `tarjetaProfesional` en create/update + exponerlo en el DTO.
- Frontend: campo **editable** "Tarjeta profesional" en la pestaña "Datos". Al
  vincular un usuario, se **prellena** desde `usuario.tarjetaProfesional` (igual
  que hoy con nombre/correo), pero luego es editable en el contrato.

## Decisiones tomadas (por el usuario)

1. **Auto-edición en Mi cuenta:** solo datos profesionales — **cédula, tarjeta
   profesional, teléfono**. Nombre/correo/contraseña los gestiona el admin.
2. **Tarjeta profesional en el contrato:** **campo propio del contrato**
   (editable; se prellena del usuario al vincular). Requiere columna nueva.
3. **Equipo en contratos:** **dejar la lista como está** (sin roster).

## Alcance

- `lex-control-api`:
  - `mi-empresa`: `GET/PATCH /mi-empresa/perfil` (+ schema zod + dto + repo).
    Los campos `Usuario.{cedula,tarjetaProfesional,telefono}` ya existen.
  - `contratos`: nueva columna `Contrato.tarjetaProfesional` (`pnpm push`);
    aceptarla en create/update; exponerla en el DTO. Al vincular usuario,
    prellenar TP desde `usuario.tarjetaProfesional` (incluir ese select).
- `lex-control-client`:
  - `cuenta/page.tsx`: tarjeta "Datos del profesional" editable (cédula, TP,
    teléfono) → `PATCH /mi-empresa/perfil`.
  - `contratos/page.tsx`: campo editable "Tarjeta profesional" en la pestaña
    Datos; prefill al vincular usuario.

## Fuera de alcance

- Validación de formato de la tarjeta profesional (es alfanumérica libre).
- Exponer estos campos en el portal admin de plataforma (ya editables ahí).

## Estado

IMPLEMENTADO (sin commit). `pnpm push` aplicado (columna `contratos.tarjeta_…`
no, mapea a `tarjetaProfesional`; DB en sync) + `pnpm generate`. tsc verde en API
y cliente. **Pendiente:** smoke real en :3001 + commit. **Gotcha:** si el API
corre en Docker, regenerar el cliente Prisma dentro del contenedor y reiniciar
(`docker exec …api pnpm generate` + restart) o `POST/PATCH /contratos` con
`tarjetaProfesional` dará 500 "Unknown argument" (ver memoria
dev-prisma-generate-en-contenedor).
