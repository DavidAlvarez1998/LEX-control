# Acción de Tutela (Recibida)

Acción de tutela presentada EN CONTRA del despacho o de su cliente: nosotros somos los **accionados**. El trámite gestiona la defensa (notificación/traslado, contestación, fallo, impugnación, segunda instancia y desacato). Normalmente deriva de un Derecho de Petición Recibido mal contestado. `clienteOpcional: true`, `esJudicial: true`, jurisdicción/grupo `CONSTITUCIONAL`.

## Fases de este caso

| Fase | Etapas (key) |
|------|--------------|
| 1. Notificación / Traslado | `traslado` (orden 0) |
| 2. Contestación | `contestacion` (orden 1) |
| 3. Fallo de 1ª instancia | `falloPrimeraInstancia` (orden 2) |
| 4. Impugnación | `impugnacion` (orden 3) |
| 5. 2ª instancia + Desacato | `falloSegundaInstancia` (orden 4, desacato como docs opcionales) |
| 6. Cierre | `terminado` (orden 5, terminal) |

No hay ramas excluyentes (no hay dos etapas con el mismo `orden`); el flujo es **lineal con etapas condicionadas por `disponibleSi`** que se saltan si no aplican. No hay `accion.crearDerivado` (no escala a otro proceso: la tutela ya es el escalamiento receptor).

## Grafo del flujo

```
0) NOTIFICACIÓN Y TRASLADO   req: radicadoTutela, accionante · doc: tutela_recibida.pdf
   ⏱ 3 días HÁBILES desde fechaNotificacion (término para contestar lo fija el juez)
        │
        ▼
1) CONTESTACIÓN DE LA TUTELA   disponibleSi contestada ∈ {SI, NO}
        ├ contestada=SI → req: fechaContestacion · doc: contestacion_tutela.pdf
        └ contestada=NO → (sin requisitos; queda sin contestar)
        │
        ▼
2) FALLO DE PRIMERA INSTANCIA   disponibleSi falloPrimera ∈ {Favorable, Desfavorable}
        │  doc: sentencia.pdf   (Favorable/Desfavorable = para el accionado/nuestra parte)
        ▼
3) IMPUGNACIÓN   disponibleSi impugnada=SI
        ├ impugnada=SI → doc: impugnacion.pdf  → sigue a 2ª instancia
        └ impugnada=NO → etapa NO disponible (se salta)
        │
        ▼
4) FALLO DE SEGUNDA INSTANCIA   disponibleSi impugnada=SI
        │  doc: sentencia_segunda.pdf
        │  opcionalesSi incidenteDesacato=SI → escrito_desacato.pdf, fallo_desacato.pdf
        ▼
5) TERMINACIÓN  ✅ terminal — "Tutela resuelta."
```

Camino mínimo (no se impugna): `traslado → contestacion → falloPrimeraInstancia → terminado` (impugnacion y falloSegundaInstancia se saltan por `disponibleSi impugnada=SI`).

## Detalle por etapa (campo por campo)

### 0) Notificación y traslado (orden 0)
- `radicadoTutela` [numero] (obligatorio)
- `accionante` [texto] (obligatorio) — quien interpuso la tutela
- `juzgado` [texto] (opcional) — juzgado que conoce
- `derechosInvocados` [textoLargo] (opcional) — derechos fundamentales invocados en su contra
- `hechos` [textoLargo] (opcional)
- `pretension` [textoLargo] (opcional)
- `fechaNotificacion` [fecha] (opcional) — ayuda: "Desde aquí corre el término para contestar (lo fija el juez)."
- **Doc requerido:** `tutela_recibida.pdf`
- **⏱ Plazo:** 3 días **hábiles** `plazoDesdeCampo: fechaNotificacion`.

### 1) Contestación de la tutela (orden 1) — `disponibleSi contestada ∈ {SI, NO}`
- `contestada` [select SI/NO] (opcional): ¿Se contestó la tutela?
  - **SI** → muestra `fechaContestacion` [fecha]; `requeridosSi`: req `fechaContestacion` + doc `contestacion_tutela.pdf`.
  - **NO** → etapa disponible pero sin requisitos (tutela sin contestar; sigue el curso).

### 2) Fallo de primera instancia (orden 2) — `disponibleSi falloPrimera ∈ {Favorable, Desfavorable}`
- `falloPrimera` [select Favorable/Desfavorable] (opcional) — ayuda: "Favorable/desfavorable para el accionado (nuestra parte)." Al fijar valor muestra `fechaFallo` [fecha].
- `fechaFallo` [fecha] (opcional, `mostrarSi falloPrimera ∈ {Favorable, Desfavorable}`).
- **Doc requerido:** `sentencia.pdf`.

### 3) Impugnación (orden 3) — `disponibleSi impugnada=SI`
- `impugnada` [select SI/NO] (opcional): ¿Se impugnó el fallo?
  - **SI** → habilita esta etapa y la de 2ª instancia; doc requerido `impugnacion.pdf`; muestra `falloSegunda`.
  - **NO** → etapa NO se ofrece; el flujo pasa directo a Terminación.
- **Doc requerido (si SI):** `impugnacion.pdf`.

### 4) Fallo de segunda instancia (orden 4) — `disponibleSi impugnada=SI`
- `falloSegunda` [select Favorable/Desfavorable] (opcional, `mostrarSi impugnada=SI`).
- `incidenteDesacato` [select SI/NO] (opcional): ¿Se promovió incidente de desacato?
  - **SI** → muestra `fechaIncidenteDesacato` [fecha]; `opcionalesSi`: docs **opcionales** `escrito_desacato.pdf`, `fallo_desacato.pdf` (no bloquean).
  - **NO** → sin docs de desacato.
- `fechaIncidenteDesacato` [fecha] (opcional, `mostrarSi incidenteDesacato=SI`).
- **Doc requerido:** `sentencia_segunda.pdf`.

### 5) Terminación (orden 5) — terminal
- Sin campos. `terminal: true`, `resultado: "Tutela resuelta."`

## Desenlaces posibles
- **Tutela resuelta** (único terminal `terminado`, resultado "Tutela resuelta."), alcanzado:
  - tras 1ª instancia sin impugnar (`impugnada=NO` salta etapas 3 y 4), o
  - tras 2ª instancia (`impugnada=SI`), con o sin incidente de desacato (docs opcionales).
- No hay terminal de archivo ni de escalamiento: este tipo es el lado receptor, no deriva a otro proceso (`accion.crearDerivado` ausente).

## Conformidad con el doc Juan David

El doc fuente (líneas ~225-231, bloque "INCIDENTE DE DESACATO" y la cola de tutela compartida por DdP/Reclamación/Renuencia) describe la tutela desde el **lado activo/peticionario** (Demanda/Pruebas/Anexos, "ADMITIERON LA TUTELA SI/NO", Auto admisorio). Este tipo modela el **lado receptor (accionados)**, por lo que las divergencias son en parte deliberadas.

**Coincidencias:**
- Radicado de la tutela [numérico] → `radicadoTutela`.
- FALLO Favorable/desfavorable + PDF de sentencia → `falloPrimera` + `sentencia.pdf`.
- IMPUGNACIÓN SI/NO → `impugnada`.
- FALLO DE SEGUNDA INSTANCIA Favorable/desfavorable → `falloSegunda` + `sentencia_segunda.pdf`.
- INCIDENTE DE DESACATO SI/NO + Fecha + Escrito PDF + Fallo PDF → `incidenteDesacato`, `fechaIncidenteDesacato`, `escrito_desacato.pdf`, `fallo_desacato.pdf` (opcionales).

**Huecos / inconsistencias:**
1. **"ADMITIERON LA TUTELA SI/NO" + "Auto admisorio PDF" + "Fecha Auto Admisorio"** (doc líneas 212-214, 35-36, 101-102): el doc tiene una fase de admisión con su auto admisorio. El seed NO la modela (no hay campo `admitida`, ni `auto_admisorio.pdf`, ni `fechaAutoAdmisorio`). El seed entra directo por "Notificación y traslado".
2. **Demanda / Pruebas / Anexos PDF** (doc 207-209): son del lado activo; el seed los reemplaza por `tutela_recibida.pdf` (correcto para receptor), pero no hay docs separados para pruebas/anexos recibidos.
3. **"SI SI- Fecha de la sentencia" / "Fecha del fallo"** (doc 218, 221): el doc pide fecha de fallo y fecha asociada a la impugnación. El seed tiene `fechaFallo` (1ª inst) pero **no** una fecha de fallo de segunda instancia ni `fechaImpugnacion`.
4. **Notificación / traslado / plazo de 3 días hábiles**: el seed añade `fechaNotificacion` + plazo 3 días hábiles para contestar. El doc no lo explicita (dice que el término lo fija el juez); el seed asume 3 días hábiles como default — posible asunción no respaldada por el doc.
5. **Contestación de la tutela** (`contestada`, `fechaContestacion`, `contestacion_tutela.pdf`): el seed la modela como etapa propia; el doc del lado receptor no la detalla explícitamente (la cola compartida del doc no incluye "contestación de la tutela" como tal). Es un añadido razonable del seed.
6. **Sin escalamiento ni cadena de caso**: a diferencia del DdP (que deriva a tutela vía `crearDerivado`), este tipo no enlaza hacia atrás al DdP Recibido que lo originó; la relación se maneja por `casoRelacionadoId` fuera de este esquema (no aparece en el seed del tipo).
