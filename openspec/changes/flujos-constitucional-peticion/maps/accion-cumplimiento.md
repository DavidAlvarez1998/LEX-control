# Acción de cumplimiento

Trámite constitucional (grupo `CONSTITUCIONAL`, jurisdicción `CONSTITUCIONAL`, área `constitucional`) en el que el despacho representa al **cliente accionante** para hacer efectivo el cumplimiento de una ley o acto administrativo por la autoridad (o particular) renuente (art. 87 C.P.; Ley 393/1997). El flujo va de la constitución de la renuencia → presentación de la demanda → admisión/traslado → sentencia → cierre.

## Fases de este caso

| Fase | Etapas (key) | Qué ocurre |
|------|--------------|------------|
| 1. Renuencia previa | `constitucionRenuenciaEtapa` | Se identifica la norma/acto incumplido, el deber omitido y la autoridad renuente; se eleva reclamo previo (requisito de procedibilidad, art. 8 Ley 393). |
| 2. Presentación | `radicacion` | Se presenta la demanda con la pretensión de cumplimiento; debe constar que la renuencia se constituyó. |
| 3. Admisión / Traslado | `admisionTraslado` | El juez admite y corre traslado a la autoridad renuente. |
| 4. Sentencia | `fallo` | El juez resuelve ordenando o negando el cumplimiento. |
| 5. Cierre | `terminado` | Terminal: cumplimiento ordenado / negado. |

## Grafo del flujo

```
1) CONSTITUCIÓN DE RENUENCIA (constitucionRenuenciaEtapa)   orden 1
       │   campos req: normaIncumplida, deberOmitido, autoridadRenuente
       │   ⏱ plazo 10 días (reclamo previo + silencio/ratificación, art. 8 Ley 393)
       ▼
2) PRESENTACIÓN DE LA DEMANDA (radicacion)                  orden 2
       │   campos req: constitucionRenuencia (¿se constituyó?), pretensionCumplimiento
       ▼
3) ADMISIÓN Y TRASLADO (admisionTraslado)                   orden 3
       │   campos req: autoridadRenuente
       │   ⏱ plazo 3 días
       ▼
4) SENTENCIA (fallo)                                         orden 4
       │   campos req: pretensionCumplimiento
       │   ⏱ plazo 20 días
       ▼
5) TERMINADO (terminado)   terminal ✔   resultado: "Cumplimiento ordenado / negado"
```

Flujo **lineal sin ramas**: las cinco etapas tienen `orden` 1→5 distintos (no hay etapas con el mismo orden, no hay decisiones excluyentes), ninguna define `disponibleSi`, `accion` ni `resultado` por opción, y no hay derivados (`crearDerivado`). El único terminal es `terminado`. No se declaran documentos (ni requeridos ni opcionales) en ninguna etapa.

## Detalle por etapa (campo por campo)

### 1) Constitución de renuencia — `constitucionRenuenciaEtapa` (orden 1)
Campos requeridos para avanzar: `normaIncumplida`, `deberOmitido`, `autoridadRenuente`.
Plazo: `plazoDias = 10` (sin `plazoDesdeCampo` ni `plazoTipoDias` declarados → días sin base/tipo explícitos en el seed; corresponde al reclamo previo + 10 días de silencio o ratificación, art. 8 Ley 393/1997).

Campos del formulario relevantes en esta etapa:
- **normaIncumplida** [textoLargo] (obligatorio) — Ley o acto administrativo incumplido.
- **deberOmitido** [textoLargo] (obligatorio) — Deber omitido por la autoridad.
- **autoridadRenuente** [texto] (obligatorio) — Autoridad o particular renuente.
- **constitucionRenuencia** [boolean] (obligatorio en el esquema; se exige como campo en la etapa siguiente) — ¿Se constituyó la renuencia? Ayuda: "Reclamo previo y silencio/ratificación en 10 días (art. 8 Ley 393/1997)."
- **fechaReclamoPrevio** [fecha] (opcional) — Fecha del reclamo previo.

Sin documentos requeridos ni opcionales.

### 2) Presentación de la demanda — `radicacion` (orden 2)
Campos requeridos para avanzar: `constitucionRenuencia`, `pretensionCumplimiento`.

- **constitucionRenuencia** [boolean] (obligatorio) — ¿Se constituyó la renuencia? (debe estar diligenciado para presentar).
- **pretensionCumplimiento** [textoLargo] (obligatorio) — Pretensión (qué cumplimiento se pide).

Sin documentos requeridos ni opcionales. Sin plazo.

### 3) Admisión y traslado — `admisionTraslado` (orden 3)
Campos requeridos para avanzar: `autoridadRenuente`.
Plazo: `plazoDias = 3` (sin `plazoDesdeCampo` ni `plazoTipoDias` declarados).

- **autoridadRenuente** [texto] (obligatorio) — Autoridad o particular renuente (a quien se corre traslado).

Sin documentos requeridos ni opcionales.

### 4) Sentencia — `fallo` (orden 4)
Campos requeridos para avanzar: `pretensionCumplimiento`.
Plazo: `plazoDias = 20` (sin `plazoDesdeCampo` ni `plazoTipoDias` declarados; corresponde al término legal para fallar de la acción de cumplimiento).

- **pretensionCumplimiento** [textoLargo] (obligatorio) — Pretensión sobre la que recae la sentencia.

Sin documentos requeridos ni opcionales. No define `resultado` por valor (no hay rama favorable/desfavorable en el seed).

### 5) Terminado — `terminado` (orden 5)
`terminal: true`. Resultado: "Cumplimiento ordenado / negado". Sin campos, sin plazos, sin documentos.

## Desenlaces posibles

1. **Terminación normal** (`terminado`, único terminal) — tras la sentencia se cierra el proceso con resultado "Cumplimiento ordenado / negado". El seed NO bifurca entre ordenado vs. negado: ambos resultados convergen en el mismo terminal único.

No hay otros desenlaces modelados: no existen ramas de inadmisión/rechazo, archivo por falta de renuencia, impugnación, segunda instancia, ni escalamiento a otro proceso (no hay `crearDerivado`).

## Notas

- **Campo del esquema sin uso en etapas**: `noGastoNuevo` [boolean] (opcional, "¿El cumplimiento NO implica gasto nuevo no presupuestado?") existe en `esquemaFormulario` pero **ninguna etapa lo lista en `camposRequeridos`** ni lo condiciona. Refleja la causal de improcedencia del art. 9 Ley 393 (no procede si genera gasto no presupuestado), pero el seed no la usa como gate ni rama; queda como dato informativo.
- **Plazos sin base ni tipo de días**: ninguna etapa con plazo (`10`, `3`, `20`) declara `plazoDesdeCampo` ni `plazoTipoDias`. A diferencia del Derecho de Petición (que ancla el plazo a `fechaRadicacion` con `plazoTipoDias = habiles`), aquí el motor no tiene fecha-base ni distinción hábiles/calendario; el plazo es un número suelto. Hueco respecto a la precisión de cómputo. Legalmente: la sentencia de cumplimiento se dicta dentro de los 20 días siguientes (art. 21 Ley 393), pero el seed no lo amarra a una fecha-campo.
- **`fechaReclamoPrevio` no alimenta el plazo de 10 días**: la etapa 1 tiene `plazoDias = 10` pero no usa `fechaReclamoPrevio` como `plazoDesdeCampo`; el plazo no se computa desde la fecha del reclamo. Hueco de modelado.
- **Sin documentos en todo el flujo**: no se exige ni se ofrece ningún PDF (demanda, reclamo previo, contestación de la entidad, auto admisorio, sentencia). A diferencia del DdP/tutela (que anclan `peticion.pdf`, `poder.pdf`, `respuesta.pdf`, etc.), la Acción de cumplimiento no captura soportes documentales. Hueco notable de modelado.
- **Sin ramas de decisión**: el flujo es estrictamente lineal. No modela inadmisión/subsanación, rechazo por falta de renuencia, ni la impugnación de la sentencia ante el superior (art. 26 Ley 393). El seed asume el camino feliz hasta sentencia + un terminal único.
- **`constitucionRenuencia` como gate**: es booleano y se exige en `radicacion`, pero el seed no impide presentar la demanda si está en `false` (sólo exige que el campo esté diligenciado, no su valor). No hay bloqueo por renuencia no constituida.
