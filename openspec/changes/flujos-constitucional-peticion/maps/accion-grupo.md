# Acción de grupo

Acción constitucional (art. 88 Const.; Ley 472/1998) para la **reparación del daño** causado a un **grupo de mínimo 20 personas** en condiciones uniformes respecto de una misma causa. El cliente del despacho actúa como **demandante** (representante del grupo) frente a la autoridad o particular causante del daño. Caduca a los **2 años** contados desde la acción u omisión dañosa.

## Fases de este caso

El flujo del seed es **lineal** (sin ramas ni decisiones): una sola cadena de 6 etapas por orden ascendente, sin `disponibleSi`, sin terminales intermedios y sin escalamiento (`crearDerivado`).

| Fase | Etapas (orden) |
|------|----------------|
| 1. Presentación | `radicacion` — Presentación de la demanda (1) |
| 2. Admisión | `admision` — Admisión (2) |
| 3. Traslado | `traslado` — Traslado al demandado (3) |
| 4. Conciliación | `audienciaConciliacion` — Audiencia de conciliación (4) |
| 5. Probatoria y sentencia | `pruebasYsentencia` — Etapa probatoria y sentencia (5) |
| 6. Cierre | `terminado` — Terminado (6, terminal) |

## Grafo del flujo

```
1) Presentación de la demanda (radicacion)
   campos req: numeroMiembrosGrupo, condicionUniforme, accionadoGrupo, hechosGrupo, pretensionGrupo
   │
   ▼
2) Admisión (admision)                               ⏱ plazoDias: 10
   campo req: dentroCaducidad   (¿se presenta dentro de los 2 años?)
   │
   ▼
3) Traslado al demandado (traslado)                  ⏱ plazoDias: 10
   campo req: accionadoGrupo
   │
   ▼
4) Audiencia de conciliación (audienciaConciliacion) ⏱ plazoDias: 5
   campo req: perjuiciosReclamados
   │
   ▼
5) Etapa probatoria y sentencia (pruebasYsentencia)  ⏱ plazoDias: 30
   campo req: pretensionGrupo
   │
   ▼
6) Terminado  [terminal] → resultado: "Indemnización ordenada / negada"
```

Sin ramas excluyentes (no hay dos etapas con el mismo `orden`), sin documentos declarados en `reglas`, y sin `plazoTipoDias` (los plazos no especifican hábiles vs. calendario — ver Notas). El boolean `dentroCaducidad` y el numero `numeroMiembrosGrupo` se piden pero no condicionan ninguna rama (ver Notas).

## Detalle por etapa (campo por campo)

### 1) Presentación de la demanda (`radicacion`) — orden 1
Campos requeridos por la etapa: `numeroMiembrosGrupo`, `condicionUniforme`, `accionadoGrupo`, `hechosGrupo`, `pretensionGrupo`.

Campos del formulario que se diligencian (esquemaFormulario):
- **Número de integrantes del grupo** `numeroMiembrosGrupo` [numero] (obligatorio) — ayuda: "Mínimo 20 personas (art. 46 Ley 472/1998)". El seed **no** valida el umbral de 20; es solo un dato (ver Notas).
- **Causa o condición uniforme del daño** `condicionUniforme` [textoLargo] (obligatorio).
- **Demandado** `accionadoGrupo` [texto] (obligatorio) — la parte demandada (autoridad o particular causante del daño).
- **Hechos** `hechosGrupo` [textoLargo] (obligatorio).
- **Perjuicios reclamados** `perjuiciosReclamados` [multiselect] (obligatorio en el formulario) — opciones: Daño emergente · Lucro cesante · Daño moral · Daño a la salud · Otro. Multiselección, no abre ramas. (Lo exige la etapa 4, no esta.)
- **Fecha de la acción u omisión dañosa** `fechaAccionUOmision` [fecha] (obligatorio en el formulario) — referencia de la caducidad de 2 años. No se usa como `plazoDesdeCampo` en ninguna etapa (ver Notas).
- **¿La demanda se presenta dentro de los 2 años?** `dentroCaducidad` [boolean] (obligatorio) — lo exige la etapa 2 (Admisión). No condiciona ninguna rama: el motor solo verifica que esté diligenciado, no su valor (ver Notas).
- **Pretensión indemnizatoria** `pretensionGrupo` [textoLargo] (obligatorio).

Documentos: ninguno declarado. Plazo: ninguno.

### 2) Admisión (`admision`) — orden 2
- Campo requerido: `dentroCaducidad`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 10` (sin `plazoDesdeCampo` ni `plazoTipoDias`).

### 3) Traslado al demandado (`traslado`) — orden 3
- Campo requerido: `accionadoGrupo`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 10`.

### 4) Audiencia de conciliación (`audienciaConciliacion`) — orden 4
- Campo requerido: `perjuiciosReclamados`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 5`.

### 5) Etapa probatoria y sentencia (`pruebasYsentencia`) — orden 5
- Campo requerido: `pretensionGrupo`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 30`.

### 6) Terminado (`terminado`) — orden 6
- `terminal: true`. `resultado: "Indemnización ordenada / negada"`.
- Sin campos, documentos ni plazo.

## Desenlaces posibles

Un único desenlace en el seed:
- **Terminado** (`terminado`, terminal) → resultado **"Indemnización ordenada / negada"** (la sentencia ordena o niega la indemnización colectiva).

No hay escalamiento a otro proceso (`crearDerivado` ausente), ni rama de archivo/inadmisión/rechazo por caducidad, ni terminación anticipada por conciliación.

## Notas

- **Flujo lineal, sin ramas.** El seed modela la Acción de grupo como una secuencia fija de 6 etapas. No hay `disponibleSi`, ni etapas con `orden` repetido (decisiones), ni acciones `crearDerivado`.
- **Plazos sin tipo de días.** Las etapas 2–5 traen `plazoDias` (10, 10, 5, 30) pero **no** `plazoTipoDias` (hábiles/calendario) ni `plazoDesdeCampo` (ancla de cómputo). Hueco frente al estándar del motor: el plazo se cuenta pero no se sabe desde qué fecha ni si son hábiles.
- **`dentroCaducidad` sin efecto de rama.** El boolean obligatorio "¿dentro de los 2 años?" lo exige la etapa Admisión, pero **ningún** `disponibleSi`/`requeridoSi` depende de su valor. Hueco: la caducidad declarada no abre una rama de rechazo (un "No" debería impedir/archivar la admisión, pero el motor solo verifica que el campo esté lleno).
- **`fechaAccionUOmision` no ancla la caducidad.** Existe la fecha de la acción dañosa pero no se usa como `plazoDesdeCampo` para computar los 2 años; el control de caducidad queda en el boolean manual `dentroCaducidad`. Hueco: el cómputo de los 2 años no está automatizado.
- **`numeroMiembrosGrupo` sin validación de umbral.** La ayuda dice "mínimo 20 personas" pero el seed no exige `>= 20` (no hay validación de rango); valor < 20 no bloquea ninguna etapa. Hueco menor.
- **`perjuiciosReclamados` exigido tarde.** El multiselect se diligencia en la demanda (etapa 1) pero como `camposRequeridos` aparece en la etapa 4 (Audiencia de conciliación), no en la radicación. Es coherente (cuantía del acuerdo), pero la asociación etapa↔campo es laxa.
- **Sin documentos.** Ninguna etapa declara `documentosRequeridos`/`documentosOpcionales` (a diferencia de tutela/DdP). No hay slots de subida (demanda en PDF, poder, anexos, auto admisorio, sentencia, listado de integrantes, etc.).
- **Conciliación sin desenlace propio.** La Ley 472/1998 prevé que la audiencia pueda terminar el proceso por acuerdo conciliatorio; el seed la modela como etapa intermedia más, sin rama de terminación por acuerdo ni resultado distinto.
- **Probatoria y sentencia fusionadas.** El seed une la etapa probatoria y la sentencia en una sola etapa (`pruebasYsentencia`), a diferencia de la Acción popular que las separa.
- **Opción "Otro" en `perjuiciosReclamados`** no abre un campo de texto libre (no hay `mostrarSi` asociado). Hueco menor.
