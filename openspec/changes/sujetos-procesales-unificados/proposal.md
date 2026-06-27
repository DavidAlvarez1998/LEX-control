# sujetos-procesales-unificados

## Por qué

En el alta de procesos de litigio (mínima cuantía, verbal, sumario) las partes se
capturaban **por triplicado** y de forma inconsistente (2026-06-27):

1. El **cliente** (arriba) → es el demandante/ejecutante y entra al CRM.
2. Campos **planos** del esquema: `demandanteNombre`, `demandanteCedula/Documento`,
   `demandanteDireccion/Correo/Telefono`, y el espejo `demandado*`.
3. El bloque **"Agregar sujeto procesal"** → la contraparte y terceros como `Litigante`
   estructurado.

El problema: **las plantillas de documentos (demanda, poder, cautelares, acuerdo,
terminación) NO consumen los campos planos** — `plantilla.ts → construirContexto()` arma
`parte.demandante` / `parte.demandado` **desde los sujetos estructurados** (el cliente
marcado `esNuestroCliente` + las partes del bloque). Los campos planos solo se mostraban en
la ficha y recibían el autollenado de la Rama. Eran captura duplicada y, peor, un footgun:
si el abogado llenaba el campo plano pero no agregaba la contraparte al bloque, el documento
salía con `[[falta: …]]` en el demandado.

## Qué cambia

### Catálogo (`prisma/seed-tipos.json`, aplicado con `pnpm seed:catalogo`)
Se **eliminan los campos planos de identidad/contacto** de las partes en:
- **Proceso ejecutivo de mínima cuantía**: `demandanteNombre`, `demandanteDocumento`,
  `demandadoNombre`, `demandadoDocumento`.
- **Proceso verbal** y **Proceso verbal sumario**: `demandante{Nombre,Cedula,Direccion,
  Correo,Telefono}` y `demandado{…}` (5+5 cada uno).

Se **conservan** los campos **procesales** que casualmente empiezan con demandante/demandado
(`demandadoNotificado`, `demandantePronuncio`, `demandanteFechaPronunciamiento`) — son de
etapa, no de identidad. Se conserva también `repLegal*` (rep. legal del cliente-empresa para
el poder). El seed reemplaza `esquemaFormulario` completo y sube `esquemaVersion`.

### UI (cliente, `procesos/nuevo`)
El bloque "Agregar sujeto procesal" se reencuadra como **"Sujetos procesales"**: el único
lugar para la contraparte (demandado/ejecutado) y los terceros, cada uno con rol, documento y
datos de notificación. El subtítulo aclara que el demandante/ejecutante es el cliente. El
demandante/demandado de los documentos sigue saliendo del par cliente + bloque.

**Posición:** el bloque vive **dentro de la tarjeta "Datos del proceso"**, como su **primer
elemento** (con divisor), justo debajo de "Abogado responsable" y antes de los campos
dinámicos. (Iteración: primero quedó como primera tarjeta del form — muy arriba — y se bajó.)

**Alta/edición en Modal:** "+ Agregar parte" ya no despliega los campos inline; abre un
**Modal** (`@/components/ui` Modal, portaleado a body) que bloquea la vista y cierra con
**Esc**, backdrop o Cancelar. La lista muestra cada sujeto como fila-resumen (nombre · rol ·
documento) con acciones *editar* / *quitar*. El borrador (`draftParte`) solo se vuelca a
`partes` al confirmar. Mismo patrón que el panel `partes-proceso.tsx` de la ficha (que ya
usaba Modal), pero contra estado local (sin API; el proceso aún no existe).

### Ficha (`procesos/[id]` + `datos-proceso.tsx`) — autollenado Rama → contraparte estructurada
El botón "Actualizar con la Rama" del campo radicado devuelve demandante/demandado. Antes los
escribía a los campos planos (ya eliminados). Ahora `DatosProceso` expone
`onAutollenarPartes`, y el padre (`[id]/page.tsx`, que tiene `proceso.partes` + `setProceso`)
**crea o completa la contraparte** como sujeto estructurado: identifica cuál de los dos es la
contraparte (la que NO es nuestro cliente, según el rol del cliente), y si no existe la crea
con `agregarParte` (rol opuesto al del cliente); si existe sin nombre la completa con
`editarParte`; si ya tiene nombre, no lo pisa. Best-effort (falla en silencio).

## Decisiones (con el usuario)
- Aplica a **todos** los tipos de litigio (mínima cuantía, verbal, sumario). **Laboral ya
  estaba así** (usa el bloque estructurado para litisconsorcio; no tenía campos planos) → es
  el modelo de referencia.
- El **cliente se deja como está** (captura aparte, enlazado al CRM). No se fusiona en una
  lista plana — esa sería una fase posterior (marcar "este es mi cliente" dentro del bloque).

## Fuera de alcance
- No se migran datos: los procesos viejos conservan los campos planos en su `datos` JSON
  (no se muestran y las plantillas no los usan).
- (Resuelto) El autollenado de la Rama en la ficha ya no escribe a campos planos: enruta a la
  contraparte estructurada (ver arriba).

## Verificación
- `seed-tipos.json` válido (JSON parse OK, 31 tipos) · identidad eliminada · procesales
  conservados.
- API `tsc` OK · client `tsc` OK · `pnpm seed:catalogo` → 31 tipos actualizados en la DB.
- Sin commit.
