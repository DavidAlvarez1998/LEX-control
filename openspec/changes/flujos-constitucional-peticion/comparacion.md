# Comparación de flujos — Peticiones · Constitucionales · (vs Laboral)

Compara los 9 tipos mapeados en `maps/` (grupos `PETICION` y `CONSTITUCIONAL`,
jurisdicción `CONSTITUCIONAL`) entre sí y contra el modelo de referencia del
**Proceso Laboral** (`openspec/changes/laboral-doble-instancia/`, doc fuente
"PROCEDIMIENTO LABORAL - CORREGIDO 15 DE JUNIO.docx"). Fuente de cada fila: el
mapa homónimo en `maps/`.

## Tabla maestra

| # | Tipo (slug) | Grupo | Etapas | Fases (modelo del tipo) | Variante "recibido" | Reiteración / recurso | Escala a otro proceso | Terminales |
|---|---|---|---|---|---|---|---|---|
| 1 | `derecho-peticion` | PETICION | 6 | Elaboración · Radicación/vencimiento · Respuesta · Reiteración · Escalamiento · Cierre | No (es el lado **saliente**; el receptor es el tipo 2) | Reiteración = nuevo DdP (solo PARCIAL); `recurso.pdf` opcional, sin etapa propia | Sí → **Acción de tutela** (`crearDerivado`, NO/PARCIAL) | 1 (`terminada` — "Petición terminada.") |
| 2 | `ddp-recibido` | PETICION | 4 | Recepción · Respuesta · Reiteración/Escalamiento · Cierre | **Sí, es la variante recibido** (cliente = receptor; plazo corre en contra) | Reiteración = nuevo DdP Recibido (PARCIAL); `recurso.pdf` opcional | Sí → **Acción de Tutela (Recibida)** (`crearDerivado`, NO/PARCIAL) | 1 (`terminada` — "Petición recibida atendida.") |
| 3 | `reclamacion-administrativa` | PETICION | 5 | Elaboración · Radicación · Respuesta · Reiteración/Escalamiento · Cierre | No | Reiteración = nueva Reclamación (PARCIAL); `recurso.pdf` opcional | Sí → **Acción de tutela** (`crearDerivado`, NO/PARCIAL) | 1 (`terminada` — "Reclamación terminada.") |
| 4 | `constitucion-renuencia` | PETICION | 5 | Elaboración · Radicación · Respuesta · Escalamiento · Cierre | No | No reitera; sin recurso propio | Sí → **Acción de tutela** (`crearDerivado`, NO/PARCIAL) | 1 (`terminada` — "Renuencia constituida.") |
| 5 | `tutela` | CONSTITUCIONAL | 7 | Radicación · Admisión · Fallo 1ª · Impugnación · Fallo 2ª · Remisión revisión · Cierre | No (lado **activo/accionante**) | Impugnación = etapa condicional (`impugnada=SI`); desacato = campo ficha | **No** (la tutela es el destino del escalamiento, no escala) | 1 (`terminado` — "Tutela resuelta…") |
| 6 | `tutela-recibida` | CONSTITUCIONAL | 6 | Traslado · Contestación · Fallo 1ª · Impugnación · Fallo 2ª+desacato · Cierre | **Sí, es la variante recibido** (somos accionados) | Impugnación = etapa condicional (`impugnada=SI`); desacato = docs opcionales | **No** (es el receptor del escalamiento) | 1 (`terminado` — "Tutela resuelta.") |
| 7 | `accion-cumplimiento` | CONSTITUCIONAL | 5 | Renuencia previa · Presentación · Admisión/traslado · Sentencia · Cierre | No | No (lineal, sin impugnación modelada) | **No** | 1 (`terminado` — "Cumplimiento ordenado / negado") |
| 8 | `accion-popular` | CONSTITUCIONAL | 6 | Presentación · Admisión/traslado · Pacto cumplimiento · Probatoria · Sentencia · Cierre | No | No (lineal) | **No** | 1 (`terminado` — "Amparada / negada") |
| 9 | `accion-grupo` | CONSTITUCIONAL | 6 | Presentación · Admisión · Traslado · Conciliación · Probatoria+sentencia · Cierre | No | No (lineal) | **No** | 1 (`terminado` — "Indemnización ordenada / negada") |

Notas transversales de la tabla:
- **Todos los tipos tienen un único terminal** (no hay terminales diferenciados por
  resultado: ordenado/negado, amparada/negada y favorable/desfavorable convergen en
  el mismo `terminado`/`terminada`).
- Las **variantes "recibido"** existen solo para Derecho de Petición (tipo 2) y Tutela
  (tipo 6). Reclamación y Renuencia **no** tienen variante recibido modelada; el doc
  Juan David sí describe una sección "RECIBIR – Derecho de Petición".
- El **escalamiento a tutela** (`crearDerivado`) es exclusivo del grupo PETICION
  (tipos 1–4). Las acciones constitucionales judiciales (5–9) **no** escalan.

## Patrones comunes

### Lo que comparten estos 9 flujos entre sí

1. **Dos arquetipos claros:**
   - **Peticiones (1–4)** = patrón *radicar → esperar respuesta → ramificar por
     `contestaron` SI/PARCIAL/NO*. Mismo esqueleto: Elaboración → Radicación (corre el
     plazo) → Respuesta → {Reiteración / Escalar a tutela} → Terminación. La
     condicionalidad vive en `disponibleSi` de etapas más `requeridosSi`/`opcionalesSi`
     de documentos; el gate maestro es el campo soloFicha `contestaron`/`contestada`.
   - **Acciones constitucionales judiciales (5–9)** = patrón *cadena procesal lineal*
     (presentación → admisión/traslado → audiencia/probatoria → sentencia → cierre). Las
     dos tutelas (5, 6) son lineales con etapas condicionadas por `disponibleSi` y
     decisiones resueltas como campos de ficha; cumplimiento/popular/grupo (7–9) son
     estrictamente lineales sin ninguna rama.

2. **Plazos en días hábiles solo en el grupo PETICION.** Los tipos 1–4 anclan el plazo
   a una fecha-campo (`fechaRadicacion`/`fechaRecepcion`) con `plazoTipoDias = habiles`
   y mapa por valor (`plazoDiasPorValorDe`: General 15 / Documental 10 / Consulta 30).
   La tutela (5) ancla solo la radicación (10 hábiles desde `fechaPresentacion`). Las
   acciones 6–9 traen `plazoDias` sueltos **sin** `plazoTipoDias` ni `plazoDesdeCampo`.

3. **Documentos anclados por campo** (slots con nombre: `peticion.pdf`, `poder.pdf`,
   `respuesta.pdf`, `demanda.pdf`, `sentencia.pdf`…) en tipos 1–6. En cambio
   cumplimiento/popular/grupo (7–9) **no declaran ningún documento** en ninguna etapa.

4. **`mostrarSi` apenas se usa.** En las peticiones la condicionalidad de campos vive
   casi toda en `disponibleSi` de etapas y `requeridosSi`/`opcionalesSi` de documentos;
   `mostrarSi` aparece de forma significativa solo en las tutelas (mostrar fechas/fallos
   según `admitida`/`falloPrimera`/`impugnada`/`incidenteDesacato`).

5. **Convención frágil de fechas:** todos los tipos del grupo PETICION coexisten con
   `fechaRadicado` (referencia, no corre plazo) vs `fechaRadicacion` (soloFicha, ancla el
   plazo) — nombres casi idénticos, fuente recurrente de confusión.

### En qué se parecen / diferencian del modelo laboral

| Dimensión | Peticiones / Constitucionales (1–9) | Proceso Laboral (referencia) |
|---|---|---|
| **1 form → ramas por opción** | Sí en peticiones (rama por `contestaron`); las acciones 7–9 son lineales sin ramas | Sí, y mucho más rico: 1 form (rol × instancia) ramifica a 4 flujos distintos vía `disponibleSi` compuestos |
| **Fases** | Implícitas (los mapas las nombran), pero **no hay etiqueta `fase` en el seed** | Definidas como esqueleto de 6 fases; propuesta de etiqueta `fase` en `EtapaDef` para el stepper agrupado |
| **`disponibleSi`** | Simple: igualdad / pertenencia a conjunto de un campo | Compuesto: `{alguna:[…]}` / `{todas:[…]}` (AND/OR), p.ej. `recurso_rechazo` alcanzable desde admisión Y subsanación |
| **`mostrarSi`** | Marginal (salvo tutelas) | Central: gobierna visibilidad de los campos de 2ª instancia, reconvención, etc. |
| **Documentos anclados** | Sí (1–6); ausentes en 7–9 | Sí, abundantes y obligatorios por etapa (demanda/auto/sentencia/apelación…) |
| **Plazos hábiles** | Bien anclados en peticiones; sueltos en acciones 6–9 | Hábiles anclados a fecha-campo (10 contestación, 5 subsanación, 3 recurso); 2ª instancia sin plazo (fiel al doc) |
| **Ramas excluyentes (mismo `orden`)** | Sí en peticiones (`reiteracion`/`escala_tutela` comparten orden) | Sí y deliberado (pares por instancia: única vs doble; subsanación vs recurso) |
| **Escalamiento (`crearDerivado`)** | Eje del grupo PETICION (→ tutela / nuevo DdP) | No usa `crearDerivado`; todo el ciclo (incl. 2ª instancia) vive dentro del mismo proceso |
| **Terminales diferenciados** | No: un terminal único por tipo | Sí: archivo (retiro/rechazo) · conciliación · terminación 1ª en firme · terminación tras 2ª |
| **Sub-flujos anidados** | No (la cadena se hace por procesos derivados encadenados) | Sí: reconvención abre un sub-flujo completo (admitir/inadmitir/rechazar + traslado) dentro de la contestación |

**Lectura:** el laboral es el modelo más maduro (condiciones compuestas, fases
explícitas, múltiples terminales, sub-flujos). Las peticiones son fieles y completas en
datos pero "ficha-céntricas" y con escalamiento por derivación; las acciones
constitucionales 7–9 son el extremo opuesto — esqueletos lineales sin documentos,
ramas ni anclas de plazo.

## Huecos e inconsistencias (consolidado)

### Prioridad ALTA (afectan corrección / cómputo / cobertura legal)

- **Plazos sin tipo ni ancla** — `plazoDias` suelto sin `plazoTipoDias` ni
  `plazoDesdeCampo`: el motor cuenta el número pero no sabe desde qué fecha ni si son
  hábiles. Afecta: `accion-cumplimiento` (10/3/20), `accion-popular` (3/3/30/20),
  `accion-grupo` (10/10/5/30), y parcialmente `tutela` (etapas posteriores 10/3/20/10
  sin `plazoTipoDias`).
- **Acciones constitucionales sin documentos** — ninguna etapa declara
  `documentosRequeridos`/`Opcionales` (ni demanda, poder, anexos, auto admisorio,
  sentencia). Afecta: `accion-cumplimiento`, `accion-popular`, `accion-grupo`. No se
  capturan soportes, a diferencia de tutela/DdP.
- **Campos "gate" que no bloquean** — booleans obligatorios que no condicionan ninguna
  rama (el motor solo verifica que estén llenos, no su valor):
  - `dentroCaducidad` en `accion-grupo` (un "No" no archiva/rechaza por caducidad).
  - `constitucionRenuencia` en `accion-cumplimiento` (renuencia no constituida no impide
    presentar).
- **`tutela-recibida` sin fase de admisión** — falta `admitida` + `auto_admisorio.pdf` +
  `fechaAutoAdmisorio` que el doc Juan David sí pide. Afecta: `tutela-recibida`.
- **Variantes del doc no modeladas como tipo** — el doc lista "RECIBIR – Derecho de
  Petición", "Reclamación Administrativa" y "Constitución de Renuencia (Ley 393)" como
  flujos; solo algunos existen como tipo. Afecta: `derecho-peticion` (reporta ausencia de
  la variante recibido en su propio tipo — cubierta por `ddp-recibido` y demás tipos
  separados, pero queda como divergencia estructural respecto al doc).

### Prioridad MEDIA (semántica de cierre / cobertura de ramas)

- **Terminal único sin diferenciar resultado** — favorable/desfavorable, ordenado/negado,
  amparada/negada convergen en el mismo terminal. Afecta: `accion-cumplimiento` (no
  bifurca ordenado vs negado), `accion-popular`, `accion-grupo`, `tutela`. Caso agudo:
  `constitucion-renuencia` cierra siempre "Renuencia constituida." incluso con
  `contestaron=SI` (cumplimiento total), donde semánticamente NO debería constituirse.
- **Cierre "silencioso" sin registrar respuesta** — `contestaron`/`contestada` es
  soloFicha y no requerido; `terminada` (orden final, sin `disponibleSi`) queda
  alcanzable aunque nunca se registre la respuesta. Afecta: `reclamacion-administrativa`,
  y por construcción los demás del grupo PETICION.
- **Sin terminal de "vencida / no respondida"** — el motor calcula vencimiento pero no
  hay etapa/resultado de petición vencida sin respuesta; único cierre = "atendida".
  Afecta: `ddp-recibido` (y aplica al patrón peticiones).
- **Terminación anticipada por acuerdo no modelada** — pacto de cumplimiento (popular) y
  audiencia de conciliación (grupo) son etapas intermedias sin rama/resultado de cierre
  por acuerdo, pese a que la Ley 472/1998 lo permite. Afecta: `accion-popular`,
  `accion-grupo`.
- **`escala_tutela` arranca casi vacío** — no copia `requierePoder` ni datos sustantivos
  (`copiarDatos` ausente; solo cliente + poder.pdf), a diferencia de `reiteracion` que sí
  copia. Afecta: `reclamacion-administrativa`, `constitucion-renuencia`, `derecho-peticion`.
- **`tutela-recibida` faltan fechas** — sin `fechaImpugnacion` ni fecha de fallo de 2ª
  instancia (solo `fechaFallo` de 1ª). Plazo de 3 días hábiles para contestar asumido sin
  respaldo del doc (que dice "lo fija el juez"). Afecta: `tutela-recibida`.
- **Sub-flujo de tutela embebido vs derivado** — el doc cuelga de NO/PARCIAL todo el
  ciclo de tutela in situ; el seed lo delega a un proceso derivado (decisión de diseño,
  pero diverge del doc). Afecta: `derecho-peticion`, `ddp-recibido`.

### Prioridad BAJA (modelado fino / metadata muerta)

- **Campos "muertos"** (existen en el form pero no condicionan nada):
  `noGastoNuevo` en `accion-cumplimiento`; `amenazaOdano` y `medidaCautelar` en
  `accion-popular`; `numeroMiembrosGrupo` (sin validar umbral ≥20) y `fechaAccionUOmision`
  (no ancla la caducidad de 2 años) en `accion-grupo`.
- **`recurso.pdf` sin etapa/derivado propio** — el doc lista RECURSO como rama de acción;
  el seed lo deja solo como documento opcional bajo PARCIAL. Afecta: `derecho-peticion`,
  `ddp-recibido`, `reclamacion-administrativa`.
- **Plazo 15 vs 10 en renuencia** — la descripción cita art. 8 Ley 393 ("10 días") pero
  la etapa usa `plazoDias: 15`. Afecta: `constitucion-renuencia`.
- **Opción "Otro" sin campo de texto libre** en multiselects (`derechosColectivos`,
  `perjuiciosReclamados`). Afecta: `accion-popular`, `accion-grupo`.
- **`radicadoRespuesta` no exigido** al marcar SI/PARCIAL (opcional/soloFicha). Afecta:
  `ddp-recibido`.
- **Campos sustantivos de la tutela agregados por el seed** (derechosFundamentales,
  hechos, pretension, etc.) que el doc trata como PDF a adjuntar, no a tipear.
  Enriquecimiento, no pérdida. Afecta: `tutela`.
- **Asociación etapa↔campo laxa / etapas fusionadas** — `perjuiciosReclamados` exigido en
  etapa 4 pese a diligenciarse en la demanda; probatoria+sentencia fusionadas en grupo
  (separadas en popular). Afecta: `accion-grupo`.

## Recomendaciones

1. **Anclar todos los plazos** — añadir `plazoDesdeCampo` + `plazoTipoDias` a las etapas
   con plazo de `accion-cumplimiento`, `accion-popular`, `accion-grupo` y a las etapas
   posteriores de `tutela`. Donde el doc calle, **preguntar** el tipo de día antes de
   asumir (ver [[plazos-dias-habiles-creele-al-doc]]).
2. **Dotar de documentos a las acciones constitucionales** — declarar slots anclados
   (demanda.pdf, poder.pdf, auto-admisorio.pdf, sentencia.pdf…) en cumplimiento/popular/
   grupo, alineándolas con el estándar de tutela/DdP.
3. **Convertir los "gates muertos" en ramas reales** — que `dentroCaducidad` (grupo) y
   `constitucionRenuencia` (cumplimiento) abran una rama de rechazo/archivo cuando el
   valor lo amerite, en vez de solo verificar que el campo esté lleno. Idem: que la
   caducidad de 2 años se compute desde `fechaAccionUOmision`.
4. **Diferenciar terminales por resultado** — separar terminación favorable/desfavorable
   (o ordenado/negado, amparada/negada) y, en `constitucion-renuencia`, evitar el literal
   "Renuencia constituida." cuando `contestaron=SI`. Considerar un terminal de "vencida /
   no respondida" para el patrón peticiones.
5. **Completar `tutela-recibida`** — agregar la fase de admisión (`admitida`,
   `auto_admisorio.pdf`, `fechaAutoAdmisorio`) y las fechas faltantes
   (`fechaImpugnacion`, fecha de fallo 2ª). Validar el plazo de 3 días para contestar
   contra el doc en vez de asumirlo.
6. **Subir la madurez al nivel laboral donde aporte** — evaluar (a) etiqueta `fase` en
   `EtapaDef` para stepper agrupado también en peticiones/constitucionales, y (b) cierre
   por acuerdo (pacto de cumplimiento / conciliación) como terminal propio en popular y
   grupo, conforme a la Ley 472/1998.
