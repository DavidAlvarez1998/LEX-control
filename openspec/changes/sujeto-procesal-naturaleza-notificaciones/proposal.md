# sujeto-procesal-naturaleza-notificaciones

## Por qué

En el alta de un sujeto procesal (contraparte/terceros) y del cliente faltaban dos cosas
para litigio real (2026-06-22):
1. Distinguir, en personas **jurídicas**, su **naturaleza** (pública / privada / mixta).
2. Poder **declarar que los datos de notificación se desconocen** (correo, dirección,
   teléfono) — relevante para emplazamiento: no es lo mismo "vacío" que "se desconocen".

## Qué cambia

### Modelo de datos (`schema.prisma`, aplicado con `pnpm push`)
- Nuevo enum `NaturalezaJuridica { PUBLICA, PRIVADA, MIXTA }`.
- `Litigante` y `Cliente`: `+ naturalezaJuridica NaturalezaJuridica?` (null si NATURAL),
  `+ correoDesconocido / direccionDesconocida / telefonoDesconocido Boolean @default(false)`.
- `Cliente`: `+ direccion String?` (antes solo tenía `ciudad`; `Litigante` ya tenía `direccion`).

### API (`procesos.schemas.ts` + `procesos.service.ts`)
- Los esquemas de litigante (crear proceso, cliente nuevo, agregar/editar parte) aceptan los
  campos nuevos. `editarParte` los incluye en el patch explícito de `updateLitigante`.
- El resto fluye por spread (`createLitigante`/`createCliente`).

### UI (cliente)
- Componente reutilizable **`Notificaciones`** (`form-ui.tsx`): correo / dirección / teléfono,
  cada uno con check **"Se desconocen los datos"** que deshabilita y limpia el campo; la marca
  se persiste. Reemplaza el bloque suelto "Correos".
- Persona **JURÍDICA** → aparece select **Naturaleza** (Pública/Privada/Mixta) y el documento
  se autoajusta a **NIT**.
- Aplicado en los 3 puntos: "Agregar sujeto procesal" y modal "Nuevo cliente" de
  `procesos/nuevo`, y el panel **Partes** de la ficha (`partes-proceso.tsx`).

## Decisiones (confirmadas con el usuario)
- Naturaleza = Pública / Privada / **Mixta**; al elegir JURÍDICA el documento se setea a NIT.
- "Se desconocen los datos" → se **persiste** la marca (no solo UI).
- Alcance = este form + ficha + cliente nuevo.

## Fuera de alcance
- Co-peticionarios (DdP) y el form del CRM de Clientes mantienen su UI previa.
- El motor de plantillas no consume aún las marcas "desconocido" (los datos quedan listos).

## Verificación
- `pnpm push` OK (DB en sync) · API `tsc` OK · client `tsc` OK · **485 tests** verdes.
- Sin commit.
