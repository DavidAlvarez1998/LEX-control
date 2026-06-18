# laboral-titulo-auto

## Por qué

Los trámites ante entidad (DdP, grupo PETICION) y las acciones constitucionales (tutela,
grupo CONSTITUCIONAL) ya **auto-generan el título** del caso al crear y ocultan el campo
manual (ver requirement *"Auto-generated case title for constitutional actions"* en el
change `tutela-form-hibrida`). El **Proceso Laboral** (grupo LABORAL, Ley 2452/2025) seguía
pidiendo el título a mano, inconsistente con esas dos vistas y con el placeholder que el
propio formulario sugería (*"Ej. Pérez vs. Aseguradora XYZ"*).

Pedido del usuario: que el título del proceso laboral se cree automáticamente, igual que en
peticiones y acciones constitucionales.

## Qué cambia

A diferencia de DdP/tutela —que son trámites **contra una entidad** (`"{tipo} — {entidad}"`)—
un proceso laboral es un **litigio entre dos partes**. Por eso su título auto sigue el patrón
legal *demandante vs. demandado*, conservando el prefijo del tipo para que sea consistente con
las otras vistas y autodescriptivo fuera de contexto (búsqueda global, notificaciones):

> **`"Proceso Laboral — {demandante} vs. {demandado}"`**

- El **orden** se deriva del campo `rol` ("Demandante" / "Demandado", a quién representamos):
  si representamos al demandado, el cliente va de segundo. Así el título queda **siempre**
  demandante-primero, sin importar el lado que llevemos.
- La **contraparte** sale de las partes cargadas (la marcada `DEMANDADO`, o la primera).
- La contraparte es **opcional** al crear: si aún no hay, el título queda solo con el cliente
  (`"Proceso Laboral — Juan Pérez"`) y se completa luego.
- El campo manual "Título del caso" se **oculta** para LABORAL (como en CONSTITUCIONAL y
  PETICION); el título **sigue editable** en la ficha.

### Roles de parte acotados a demandante/demandado
El selector genérico "Rol procesal del cliente" (y el de la contraparte) listaba **todos** los
`RolParte` de todas las jurisdicciones (ejecutante, accionante, imputado, acusado, víctima…).
Para un proceso laboral —ordinario entre dos partes— solo aplican **Demandante / Demandado**;
el resto pertenece a otras jurisdicciones. Para grupo LABORAL ambos selectores se acotan a esas
dos opciones (helper `rolesDisponibles(tipo)`).

> Pendiente de decisión del usuario (no incluido aquí): el laboral pide el lado **dos veces**
> — "Rol procesal del cliente" (arma la parte) y "Rol en el proceso" (ramifica el flujo, campo
> del esquema). Es redundante; se puede unificar en un cambio aparte.

Solo presentación del formulario de creación cliente (`/procesos/nuevo`, reusado por
`/procesos-laborales/nuevo`). No toca el motor, el schema ni la API.

## Impacto

- Specs: `tramite-catalog` (modifica el requirement del título auto para incluir LABORAL).
- Código: `lex-control-client/src/app/(dashboard)/procesos/nuevo/page.tsx`
  (condición `tituloAuto`, helper `tituloLaboral`, gate de visibilidad del campo manual).
- Supera la cláusula del change `tutela-form-hibrida` que decía que los judiciales laborales
  conservaban el título manual.
