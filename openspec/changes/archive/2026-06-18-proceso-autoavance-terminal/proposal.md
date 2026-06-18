# proceso-autoavance-terminal

## Por qué

El motor ya auto-avanza el proceso al guardar datos (`autoavanzarEtapas` →
`siguienteEtapaAuto`): camina nivel por nivel y mueve la etapa cuando la siguiente tiene sus
campos y documentos requeridos completos. Funciona para el avance normal y ya cierra el DdP en
"Terminación" cuando la respuesta es "Sí".

Pero el avance es **conservador**: se detiene en cuanto una etapa intermedia tiene un requisito
sin cumplir. Eso choca con las **decisiones terminales**: si el usuario marca *retiro de la
demanda (art. 67) = SÍ*, el proceso **debería archivarse de una**, aunque todavía no haya
subido el auto de calificación o la notificación — esos pasos ya no importan, el proceso se
retira. Hoy no salta hasta el archivo porque la admisión intermedia le pide documentos.

El usuario lo pidió así: *"si doy en retiro de la demanda, que avance hasta allí
automáticamente; así con todos los demás casos"*.

## Qué cambia

Se agrega un **salto a terminal decidido**: al guardar, si existe una etapa **terminal** cuyo
`disponibleSi` ya se cumple con los datos, está **por delante** de la etapa actual, es **única**
(no hay otro terminal compitiendo) y cumple **sus propios** requisitos (normalmente ninguno),
el proceso **avanza directo a ese terminal** — sin exigir el papeleo de las etapas intermedias
que quedan saltadas.

- Se usa como **respaldo** del avance conservador: primero corre `siguienteEtapaAuto` (sin
  cambios); si éste no avanza, se intenta el salto a terminal decidido.
- Solo aplica a terminales **con `disponibleSi`** (decisión explícita): `archivado`
  (retiro art. 67), `archivado_rechazo` (rechazo sin recurso / recurso desfavorable),
  `terminada_conciliacion` (conciliación). NO aplica a `terminada` (fin natural sin condición),
  que sigue requiriendo recorrer el flujo.
- Si hay **dos** terminales con condición satisfecha (datos contradictorios) → no salta (deja
  la decisión al usuario). Seguridad.

Es **general** (todos los tipos de proceso), no solo laboral: cualquier terminal con
`disponibleSi` se beneficia (p. ej. archivos por decisión).

## Impacto

- **Motor (API):** `procesos.router.ts` — nueva función `terminalDecidido(...)` usada como
  fallback dentro de `autoavanzarEtapas`. `siguienteEtapaAuto` **no cambia**.
- **Specs:** `tramite-management` (regla de auto-avance a terminal decidido).
- **Sin cambios de schema ni de seed.** Frontend sin cambios (el botón "Guardar y archivar/
  finalizar" ya existe; ahora el guardado efectivamente cierra el proceso).
- **Compatibilidad:** el avance conservador existente queda intacto; esto solo agrega un caso
  que antes se quedaba corto. No afecta procesos sin terminales condicionados.

## Decisión

Confirmado con el usuario: el guardado debe **reflejar el estado** que implican los datos; en
particular, las decisiones terminales (retiro/rechazo/conciliación) cierran el proceso al
guardar, sin pedir el papeleo de pasos que ya no aplican.
