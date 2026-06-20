# Proceso civil ejecutivo de mínima cuantía — diseño del flujo

> Estado: **APLICADO + VERIFICADO** (seed + re-seed + 456 tests API + build cliente +
> simulación de 5 flujos del motor). Sin commit.
> Fuente: `openspec/roadmap-docs/Proceso_Ejecutivo_Minima_Cuantia.docx`.

## 0. Dirección acordada

- En **Ordinaria · Civil** hoy hay dos categorías: **Declarativo** y **Ejecutivo**.
- Dentro de **Ejecutivo**: se **crea** el tipo **"Ejecutivo · mínima cuantía"** y
  se **quita el "Ejecutivo" genérico** (hoy `Proceso ejecutivo (singular o mixto)`,
  `nombreVisual: "Ejecutivo"`).
- **Primero** validamos el flujo (este documento). **Después** se construye el seed.

⚠️ **A verificar antes de quitar el genérico**: si existen procesos creados con el
tipo "Ejecutivo" actual, hay que migrarlos o conservar el tipo. (Decisión 4.)

## 1. Qué es (fiel al documento)

Guía práctica paso a paso del **proceso civil ejecutivo de mínima cuantía**, de la
radicación a la terminación. El doc trae, por cada paso, un **recuadro para pegar
pantallazo como evidencia** → el énfasis es **seguir el caso por etapas y adjuntar
evidencia/documentos en cada una**.

## 2. Flujo que entiendo — etapas, pasos, documentos e información por etapa

Leyenda: **Docs** = archivos a adjuntar (incluida la "evidencia/pantallazo" del
doc). **Info** = datos a capturar en el formulario de la etapa.

### Etapa 1 · `radicacion` — Radicación de la demanda ejecutiva
- **Paso:** se radica la demanda ejecutiva ante el juzgado competente con los
  documentos base.
- **Docs:** Poder · Demanda con el título ejecutivo · Solicitud de medidas
  cautelares · *(evidencia: pantallazo del envío/radicación y anexos)*.
- **Info:** demandante (nuestro cliente) y demandado · tipo de título ejecutivo
  (pagaré/letra/factura/…) · obligación clara, expresa y exigible · capital
  adeudado · interés moratorio · fecha de exigibilidad · cuantía (mínima) ·
  medidas cautelares solicitadas (cuentas / salarios / vehículos / inmuebles…).

### Etapa 2 · `radicacionJuzgado` — Radicación en el juzgado
- **Paso:** el sistema asigna el proceso a un juzgado; llega constancia con el
  nombre del juzgado y el número de radicado.
- **Docs:** constancia de radicado / acta de reparto · *(evidencia)*.
- **Info:** número de radicado · juzgado asignado · fecha de radicación.

### Etapa 3 · `calificacion` — Calificación (Admite / Inadmite) — **rama**
- **Paso:** el juez califica:
  - **ADMITE** → auto admisorio + decreta y libra las medidas cautelares.
  - **INADMITE** → término para subsanar → corregida, vuelve a calificarse.
- **Docs:** auto admisorio **o** auto inadmisorio · (si inadmite) escrito de
  subsanación · *(evidencia)*.
- **Info:** resultado (admite/inadmite) · fecha del auto · (si inadmite) causal +
  plazo de subsanación · (si admite) cautelares decretadas.

### Etapa 4 · `notifCautelares` — Notificación de las medidas cautelares
- **Paso:** se notifican/comunican las medidas a quien corresponda (demandado o
  empresa, Tránsito para vehículos, bancos para cuentas, oficinas de registro);
  el juzgado deja constancia de los oficios librados.
- **Docs:** oficios librados (bancos / tránsito / registro) · constancias de
  notificación · *(evidencia)*.
- **Info:** entidades oficiadas · fecha de cada oficio · estado de cada medida.

### Etapa 5 · `mandamientoPago` — Mandamiento de pago y notificación — **rama**
- **Paso:** se libra mandamiento de pago y se notifica al demandado:
  - **CONTESTA / propone excepciones** → continúa hacia audiencia.
  - **NO contesta** → queda en firme → sigue la ejecución.
- **Docs:** auto de mandamiento de pago · constancia de notificación al demandado ·
  (si contesta) escrito de excepciones · *(evidencia)*.
- **Info:** fecha del mandamiento · fecha de notificación · ¿contestó? (sí/no) ·
  excepciones propuestas.

### Etapa 6 · `impulsos` — Impulsos procesales
- **Paso:** actuaciones para avanzar: memoriales, oficios, solicitudes de avalúo
  y remate, requerimientos al juzgado.
- **Docs:** memoriales · solicitudes de avalúo/remate · oficios · *(evidencia)*.
- **Info:** descripción del impulso · fecha.

### Etapa 7 · `acuerdoPagos` — Posible acuerdo de pagos *(transversal/opcional)*
- **Paso:** en cualquier etapa las partes pueden acordar pago/conciliación, total
  o por cuotas, y presentarlo al juzgado.
- **Docs:** acuerdo de pago / acta de conciliación · *(evidencia)*.
- **Info:** tipo (total/cuotas) · montos · fechas · estado de cumplimiento.

### Etapa 8 · `terminacion` — Terminación del proceso — **terminal**
- **Paso:** termina por **pago total**, por **sentencia que ordena seguir la
  ejecución y rematar**, o por **cumplimiento del acuerdo**.
- **Docs:** auto / sentencia de terminación · *(evidencia)*.
- **Info:** causa de terminación · fecha.

### Etapa 9 · `desistimientoTacito` — Desistimiento tácito — **terminal alternativo**
- **Paso:** si el demandante no impulsa dentro del término legal, el juez puede
  declarar el desistimiento tácito (**art. 317 CGP**), terminando la actuación.
- **Docs:** auto que declara el desistimiento tácito · *(evidencia)*.
- **Info:** fecha del auto · motivo.

### Resumen de ramas
```
1 radicacion → 2 radicacionJuzgado → 3 calificacion
       ├─ INADMITE → subsanar → vuelve a 3
       └─ ADMITE → 4 notifCautelares → 5 mandamientoPago
                       ├─ CONTESTA → audiencia → 6 impulsos
                       └─ NO CONTESTA → ejecución → 6 impulsos
6 impulsos → 8 terminacion (terminal)
[7 acuerdoPagos: en cualquier etapa]   [9 desistimientoTacito: terminal alternativo]
```

## 2.bis Decisiones tomadas (✓)

- **Acuerdo y desistimiento = cerrar con motivo** (no son etapas de la fila). Se
  modela como **etapa terminal `terminacion`** con campo `motivoTerminacion`
  (select: *Pago total* / *Sentencia: seguir ejecución y remate* / *Acuerdo
  cumplido* / *Desistimiento tácito art. 317 CGP*) + `fechaTerminacion` + doc.
  Al llegar a terminal, el motor pone `estado = CERRADO`.
- **Plazos**: se reusan los del **proceso laboral**. En concreto, **subsanación =
  5 días hábiles** desde `fechaAdmision` (`plazoDesdeCampo` + `plazoTipoDias:
  "habiles"` + `plazoDias: 5`). Ajustable luego.
- **Borrar el "Ejecutivo" genérico**: sí, sin migración (el usuario confirmó "no
  importa"). ⚠️ El seed **no borra** tipos huérfanos → la eliminación del tipo
  actual en BD es un **paso explícito** (script/SQL), no basta con quitarlo del
  JSON.
- **Evidencia por etapa**: NO requiere UI nueva. El grupo `JUDICIAL` ya ancla
  documentos inline bajo el campo de cada etapa (`anclasPorCampo` en
  `datos-proceso.tsx`). Se logra declarando `documentosRequeridos` por etapa.

## 3. Decisiones pendientes (para resolver juntos)

1. **¿El flujo de arriba es correcto?** ¿agrego/quito/renombro etapas, docs o
   campos?
2. **Acuerdo (7) y desistimiento (9):** ¿etapas del flujo o "cerrar proceso con
   motivo" (terminales alternativos)? Recomiendo terminales alternativos.
3. **Plazos:** el doc no fija términos. ¿Dejo etapas sin plazo, o me pasas los del
   CGP a enforzar (excepciones, subsanar, desistimiento art. 317)? — hábiles o
   calendario **según el doc fuente**.
4. **Quitar el "Ejecutivo" genérico:** ¿hay procesos creados con él? Si sí,
   ¿migrar a mínima cuantía, o conservarlo? (No se borra a ciegas.)
5. **Evidencia por paso:** ¿basta la lista de documentos adjuntos del proceso
   (ya existe), o quieres la evidencia **anclada a cada etapa** (pantallazo por
   paso, como el doc)? Lo segundo es más trabajo de UX.
6. **Campos del formulario:** ¿reuso los del ejecutivo existente (título, capital,
   interés, exigibilidad, cuantía, garantía, cautelares) o un set propio?

## 4. Plan de implementación (tras aprobar — aún NO ejecutado)

1. **Esqueleto** primero: crear el tipo "Ejecutivo · mínima cuantía"
   (`ORDINARIA_CIVIL`, `categoriaSlug: ejecutivo`, única instancia) y resolver el
   "Ejecutivo" genérico (decisión 4).
2. **Seed del flujo** (`seed-tipos.json`): las 9 etapas con ramas
   (admite/inadmite, contesta/no contesta), `camposRequeridos` y
   `documentosRequeridos` por etapa.
3. (Opcional, decisión 5) evidencia anclada por etapa en la UI.
4. **Verificar:** simular flujos (admite→terminación; inadmite→subsanar; no
   contesta→ejecución; desistimiento) contra el motor; re-seed; build.

> Nada ejecutado. Espero tu visto bueno al flujo (sección 2) y a las decisiones.
