# Addendum — Gate "¿Hubo audiencia?" en la etapa audiencia (art. 392)

## Por qué

En el ejecutivo de mínima cuantía con excepciones, la causa se tramita por verbal sumario:
hay **audiencia única (art. 392)** donde se resuelven las excepciones y se dicta sentencia. Hoy la
etapa `audiencia` muestra/exige **siempre** `fechaAudiencia` y el documento `acta-audiencia.pdf`,
aunque la audiencia **todavía no se haya realizado**. Igual que hicimos con la sentencia
(`huboSentencia`), falta un **gate "¿Hubo audiencia?"** que despliegue lo de la audiencia solo cuando
ocurrió. Es una **refactorización** del bloque, no campos nuevos de fondo: ya existen `fechaAudiencia`
y `acta-audiencia.pdf`; solo se agrega el gate y se vuelven condicionales.

## Diseño

### Cascada (orden y dependencia)

Dentro de la etapa `audiencia` (`disponibleSi: contesto = Sí`), de arriba a abajo:

```
Excepciones propuestas            (excepcionesPropuestas)        + doc excepciones.pdf   [contesto=Sí]
¿Hubo audiencia? (Sí/No)          (huboAudiencia)  ── NUEVO gate                          [contesto=Sí]
   └─ Fecha de la audiencia       (fechaAudiencia)               + doc acta-audiencia.pdf [huboAudiencia=Sí]
¿Hubo sentencia? (Sí/No)          (huboSentencia)                                          [huboAudiencia=Sí]
   └─ Decisión sobre las excepciones  (decisionExcepciones)                                [huboSentencia=Sí]
   └─ Sentencia sobre las excepciones (sentenciaExcepciones)     + doc sentencia.pdf       [huboSentencia=Sí]
```

**Decisión clave (encadenamiento):** `huboSentencia` pasa a depender de `huboAudiencia = Sí` (no hay
sentencia sin audiencia — art. 392 audiencia única). Antes dependía solo de `contesto`. Así la cadena
es: `contesto → huboAudiencia → fechaAudiencia` y `huboAudiencia → huboSentencia → decisión/sentencia`.

### `mostrarSi` por campo (UI)

| campo | mostrarSi |
|---|---|
| `excepcionesPropuestas` | `contesto = Sí` |
| `huboAudiencia` (nuevo) | `contesto = Sí` |
| `fechaAudiencia` | `contesto = Sí` **y** `huboAudiencia = Sí` |
| `huboSentencia` | `contesto = Sí` **y** `huboAudiencia = Sí` |
| `decisionExcepciones` | `contesto = Sí` **y** `huboSentencia = Sí` |
| `sentenciaExcepciones` | `contesto = Sí` **y** `huboSentencia = Sí` |

### Reglas de etapa (solo los DOCUMENTOS son condicionales)

**Decisión de implementación:** los CAMPOS se quedan en `camposRequeridos` fijos (no se mueven a
`requeridosSi`). Razón: (a) `requisitosListos` (maquina-etapas.ts) NO respeta `mostrarSi`, y (b) la
ficha (`seccionesPorEtapa`) ancla a la sección por `camposRequeridos`/condiciones — al moverlos a
`requeridosSi.camposRequeridos` quedaban sin anclar y caían en otras secciones (mandamientoPago /
impulsos). Solo se vuelven condicionales los DOCUMENTOS (que es el objetivo: no exigir acta/sentencia
antes de que existan). La visibilidad de los campos la maneja `mostrarSi`.

```jsonc
"reglas": {
  "camposRequeridos": ["excepcionesPropuestas", "huboAudiencia", "fechaAudiencia",
                       "huboSentencia", "decisionExcepciones", "sentenciaExcepciones"],
  "documentosRequeridos": ["excepciones.pdf"],                       // fijo
  "requeridosSi": [
    { "si": { "campo": "huboAudiencia", "igualA": "Sí" },
      "documentosRequeridos": ["acta-audiencia.pdf"] },              // solo si hubo audiencia
    { "si": { "campo": "huboSentencia", "igualA": "Sí" },
      "documentosRequeridos": ["sentencia.pdf"] }                    // solo si hubo sentencia
  ]
}
```

### Anclaje de sección (ficha agrupa por etapa)

Todos los campos están en `camposRequeridos` de la etapa `audiencia` → `seccionesPorEtapa` los ancla a
la sección "Audiencia" (verificado por simulación: los 6 caen en `audiencia`). Los documentos
condicionales: el cliente (`anclasPorCampo`) ancla `acta-audiencia.pdf` y `sentencia.pdf` bajo el campo
de su condición (`huboAudiencia` / `huboSentencia`) cuando ésta se cumple.

### No destructivo

El motor lee el **valor** de los campos aunque estén ocultos, así que el enrutamiento de etapas
(`terminado_excepciones` si `sentenciaExcepciones = Prosperan`; impulsos/remate si `No prosperan`)
sigue intacto. Procesos legacy con `fechaAudiencia`/sentencia ya cargados: marcar
`huboAudiencia = Sí` (y `huboSentencia = Sí`) los vuelve a mostrar.

## Verificación (al implementar)

- `node -e JSON.parse` del seed; `pnpm seed:catalogo` → bump de `esquemaVersion`.
- Simular `seccionesPorEtapa` + `campoVisible` con `datos` en 3 estados (sin audiencia / audiencia sí
  sin sentencia / audiencia+sentencia) → todos en sección "audiencia", visibilidad correcta.
- `pnpm vitest run tests/ejecutivo-flujos.test.ts tests/procesos.test.ts`.

## Rollback

Revertir el bloque `reglas` de la etapa `audiencia` y los `mostrarSi` de `fechaAudiencia`/
`huboSentencia` a su estado previo; quitar el campo `huboAudiencia`.
