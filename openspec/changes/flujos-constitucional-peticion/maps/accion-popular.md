# Acción popular

Acción constitucional (art. 88 Const.; Ley 472/1998) que protege **derechos e intereses colectivos** (ambiente sano, moralidad administrativa, espacio público, patrimonio público, salubridad, etc.). El cliente del despacho actúa como **actor popular** (demandante) frente a la autoridad o particular que amenaza o vulnera el derecho colectivo. Admite medidas cautelares y la figura del pacto de cumplimiento.

## Fases de este caso

El flujo del seed es **lineal** (sin ramas ni decisiones): una sola cadena de 6 etapas por orden ascendente, sin `disponibleSi`, sin terminales intermedios y sin escalamiento (`crearDerivado`).

| Fase | Etapas (orden) |
|------|----------------|
| 1. Presentación | `radicacion` — Presentación de la demanda (1) |
| 2. Admisión y traslado | `admisionTraslado` — Admisión y traslado (2) |
| 3. Pacto de cumplimiento | `pactoCumplimiento` — Audiencia de pacto de cumplimiento (3) |
| 4. Probatoria | `pruebas` — Etapa probatoria (4) |
| 5. Sentencia | `sentencia` — Sentencia (5) |
| 6. Cierre | `terminado` — Terminado (6, terminal) |

## Grafo del flujo

```
1) Presentación de la demanda (radicacion)
   campos req: derechosColectivos, accionadoPopular, hechosPopular, pretensionPopular
   │
   ▼
2) Admisión y traslado (admisionTraslado)            ⏱ plazoDias: 3
   campo req: accionadoPopular
   │
   ▼
3) Audiencia de pacto de cumplimiento (pactoCumplimiento)   ⏱ plazoDias: 3
   campo req: pretensionPopular
   │
   ▼
4) Etapa probatoria (pruebas)                        ⏱ plazoDias: 30
   campo req: hechosPopular
   │
   ▼
5) Sentencia (sentencia)                             ⏱ plazoDias: 20
   campo req: pretensionPopular
   │
   ▼
6) Terminado  [terminal] → resultado: "Amparada / negada"
```

Sin ramas excluyentes (no hay dos etapas con el mismo `orden`), sin documentos declarados en `reglas`, y sin `plazoTipoDias` (los plazos no especifican hábiles vs. calendario — ver Notas). El único campo `boolean` del formulario (`medidaCautelar`) no condiciona ninguna etapa.

## Detalle por etapa (campo por campo)

### 1) Presentación de la demanda (`radicacion`) — orden 1
Campos requeridos por la etapa: `derechosColectivos`, `accionadoPopular`, `hechosPopular`, `pretensionPopular`.

Campos del formulario que se diligencian (esquemaFormulario):
- **Derechos o intereses colectivos invocados** `derechosColectivos` [multiselect] (obligatorio) — opciones: Ambiente sano · Moralidad administrativa · Espacio público · Patrimonio público · Salubridad pública · Seguridad y prevención de desastres · Acceso a servicios públicos · Patrimonio cultural · Libre competencia económica · Derechos de los consumidores y usuarios · Otro. Multiselección, no abre ramas.
- **Autoridad o particular accionado** `accionadoPopular` [texto] (obligatorio) — la parte demandada (autoridad pública o particular).
- **Hechos** `hechosPopular` [textoLargo] (obligatorio).
- **¿Es amenaza o daño ya causado?** `amenazaOdano` [select] (obligatorio en el formulario) — opciones: Amenaza · Daño contingente · Vulneración / daño causado. No condiciona campos ni etapas (puramente descriptivo).
- **Pretensión** `pretensionPopular` [textoLargo] (obligatorio).
- **¿Se solicita medida cautelar?** `medidaCautelar` [boolean] (opcional) — no condiciona ninguna etapa ni documento en el seed.

Documentos: ninguno declarado. Plazo: ninguno.

### 2) Admisión y traslado (`admisionTraslado`) — orden 2
- Campo requerido: `accionadoPopular`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 3` (sin `plazoDesdeCampo` ni `plazoTipoDias`).

### 3) Audiencia de pacto de cumplimiento (`pactoCumplimiento`) — orden 3
- Campo requerido: `pretensionPopular`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 3`.

### 4) Etapa probatoria (`pruebas`) — orden 4
- Campo requerido: `hechosPopular`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 30`.

### 5) Sentencia (`sentencia`) — orden 5
- Campo requerido: `pretensionPopular`.
- Documentos: ninguno. ⏱ Plazo: `plazoDias: 20`.

### 6) Terminado (`terminado`) — orden 6
- `terminal: true`. `resultado: "Amparada / negada"`.
- Sin campos, documentos ni plazo.

## Desenlaces posibles

Un único desenlace en el seed:
- **Terminado** (`terminado`, terminal) → resultado **"Amparada / negada"** (la sentencia ampara o niega la protección de los derechos colectivos).

No hay escalamiento a otro proceso (`crearDerivado` ausente), ni rama de archivo/inadmisión, ni terminación anticipada por pacto de cumplimiento.

## Notas

- **Flujo lineal, sin ramas.** El seed modela la Acción popular como una secuencia fija de 6 etapas. No hay `disponibleSi`, ni etapas con `orden` repetido (decisiones), ni acciones `crearDerivado`.
- **Plazos sin tipo de días.** Las etapas 2–5 traen `plazoDias` (3, 3, 30, 20) pero **no** `plazoTipoDias` (hábiles/calendario) ni `plazoDesdeCampo` (ancla de cómputo). Hueco frente al estándar del motor: el plazo se cuenta pero no se sabe desde qué fecha ni si son hábiles.
- **`amenazaOdano` muerto en el flujo.** El select obligatorio Amenaza/Daño contingente/Vulneración no condiciona ningún campo, documento ni etapa (no hay `mostrarSi`/`requeridoSi` que lo usen). Es solo metadato de la demanda.
- **`medidaCautelar` sin efecto.** La descripción del tipo dice "admite medidas cautelares", y el formulario tiene el boolean `medidaCautelar`, pero ninguna etapa, documento ni regla depende de él. Hueco: la medida cautelar declarada no abre etapa ni requisito.
- **Sin documentos.** Ninguna etapa declara `documentosRequeridos`/`documentosOpcionales` (a diferencia de tutela/DdP). No hay slots de subida (demanda en PDF, poder, anexos, auto admisorio, sentencia, etc.).
- **Pacto de cumplimiento sin desenlace propio.** La Ley 472/1998 prevé que el pacto de cumplimiento pueda terminar el proceso por acuerdo; el seed lo modela como una etapa intermedia más, sin rama de terminación por acuerdo ni resultado distinto.
- **`opciones "Otro"` en `derechosColectivos`** no abre un campo de texto libre (no hay `mostrarSi` asociado). Hueco menor.
