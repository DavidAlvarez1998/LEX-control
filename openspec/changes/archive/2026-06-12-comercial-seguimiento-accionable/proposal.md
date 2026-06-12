# comercial-seguimiento-accionable

## Por qué

El módulo comercial del portal cliente **captura** lo correcto (embudo de 9 fases, bitácora de
contactos `SeguimientoComercial`, cotización/contrato/cobro, 7 alertas derivadas, agenda), pero
**no impulsa el trabajo diario** del comercial — que es el propósito del seguimiento:

- La lista de clientes no muestra señales de seguimiento (última gestión, próxima tarea, días sin
  contacto, fase): no se puede leer el pipeline de un vistazo.
- Las alertas del Inicio son conteos muertos (sin drill-down ni acción).
- Registrar un contacto y agendar el siguiente paso están fragmentados; no hay vista "¿a quién
  contacto hoy?".
- El resultado de cada gestión es texto libre → el embudo no es medible.

No falta data: falta **exponerla y cerrarle el ciclo**.

## Qué cambia

1. **Disposición tipificada de la gestión.** Enum `DisposicionGestion { CONTACTADO, NO_CONTESTA,
   INTERESADO, NO_VIABLE, OTRO }` + columna nullable `disposicion` en `SeguimientoComercial`
   (aditivo, `db push`). Hace medible el embudo y alimenta la señal frío/caliente. Se persiste en
   POST/PATCH de seguimiento.

2. **Señales derivadas + pipeline.** `GET /comercial/pipeline` devuelve los clientes con campos
   calculados on-read (NO se guardan): `ultimaGestionEn`/`diasSinGestion`, `proximaTareaEn`/
   `tareaVencida`, `faseActual`/`diasEnFase`, `ultimaDisposicion`. Filtros `?frio`/`?vencidas`/
   `?fase`/`?mios`. Reusa el patrón de derivación on-read de las alertas y el scoping
   `soloMisClientes`.

3. **Cockpit "Para hoy".** `GET /comercial/hoy` agrupa 3 buckets accionables: `vencidas` (tareas
   pendientes con `fechaProximaTarea < hoy`), `hoy` (vence hoy; incluye citas REUNION/VIDEOLLAMADA),
   `frios` (PROSPECTO con `diasSinGestion ≥ 3` sin próxima tarea). Cada item trae lo necesario para
   actuar (cliente nombre/telefono, fase, tarea). Nueva ruta cliente `/seguimiento` con acciones de
   1 clic (Llamar `tel:`, WhatsApp `wa.me`, Registrar gestión, Abrir ficha).

4. **Cerrar el ciclo.** Formulario único de registrar gestión (en ficha y cockpit) captura
   `tipoGestion` + `disposicion` + `resultado` + próximo paso (`proximaTarea` + `fechaProximaTarea`).
   Si hay fecha → queda como tarea de agenda; si `disposicion = NO_VIABLE` → atajo "marcar fase
   PERDIDO" (reusa `POST /clientes/:id/fase`).

5. **Lista y alertas accionables.** `/clientes` muestra las señales derivadas + filtros rápidos. El
   panel "Pendientes" del Inicio deja de ser conteos: cada alerta enlaza al cockpit / `/clientes`
   filtrado. `GET /comercial/alertas` enriquece cada item con `nombre` (+ `telefono`).

## Impacto

- Schema: +1 enum (`DisposicionGestion`), +1 columna nullable (`seguimientos_comerciales.disposicion`).
  Aplicado con `db push` (sin migración; ver db-not-managed-by-migrate). Sin backfill.
- API: +2 endpoints de lectura (`/comercial/pipeline`, `/comercial/hoy`); enriquecer `/comercial/alertas`;
  persistir `disposicion`. Sin nuevos permisos (reusa `comercial.seguimiento.ver`/`comercial.alertas.ver`).
- Frontend: nueva ruta `/seguimiento` + nav; enriquecer `/clientes`; componente reutilizable
  `registrar-gestion`; Inicio accionable.

## Capabilities (specs)

- MODIFIED: `comercial-seguimiento` (campo disposicion + cerrar ciclo), `comercial-alertas`
  (items accionables), `clientes` (señales en la lista).
- ADDED: `comercial-pipeline` (señales derivadas por cliente + cockpit "Para hoy").
