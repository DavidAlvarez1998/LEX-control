# ux-rama-judicial-minima-cuantia

## Por qué

El **proceso ejecutivo de mínima cuantía** es el único tipo hoy **conectado de punta a punta**
con la API de la Rama Judicial (CPNU): radicado → idProceso → actuaciones, autollenado de juzgado +
fecha, sugerencias de hito, "nuevas" persistentes y aviso por correo (ver [[rama-judicial-actuaciones]]).
Ya **funciona**. Este change **analiza la UI/UX de esa parte y propone mejoras** — aprovechando todo
lo que la API permite (incluida la superficie aún no consumida: Detalle, Sujetos, Documentos, Descarga
de PDFs). **Solo diseño**: identificar, priorizar y proponer. **NO** se modifica código.

Alcance: el flujo del usuario abogado alrededor de un proceso judicial con radicado — **lista** de
procesos, **creación**, y sobre todo la **ficha** (donde vive la integración). Arranca en mínima
cuantía, pero casi todo generaliza a cualquier `Proceso` judicial con radicado.

## Qué entrega este change (solo documentos)

- `analisis-estado-actual.md` — mapa de la UI/UX de hoy (lista · creación · ficha) y los **gaps**.
- `propuestas-ux.md` — propuestas concretas, **priorizadas** (impacto × esfuerzo), con bocetos ASCII,
  qué capacidad de la API/back habilita cada una, y un **roadmap por fases**.

## Resumen de hallazgos (los 5 más importantes)

1. **Las novedades del juzgado solo se ven entrando a cada ficha.** No hay señal en la **lista** →
   el abogado no sabe qué procesos tienen actuaciones nuevas sin abrirlos uno por uno. *(gap A)*
2. **Dos "líneas de tiempo" que se confunden:** las *etapas internas* (lo que gestiona el despacho)
   vs. las *actuaciones del juzgado* (lo que publica la Rama). Mismo aspecto, significado distinto. *(gap L/B)*
3. **Frescura desconocida:** no se ve "última sincronización hace X" ni qué tan al día está el dato. *(gap C)*
4. **Desaprovechamos media API:** podemos traer **Detalle** (tipo/clase/ubicación), **Sujetos**
   (partes estructuradas) y **descargar los PDF reales del expediente** — nada de eso está en la UI.
5. **Confianza:** la Rama no es tiempo real (latencia de días, procesos reservados, juzgados que no
   publican). La UI no comunica esos estados ni el "verifica con el juzgado para lo crítico". *(gap C/M + validación legal)*

## Lo que NO hace este change

No implementa nada. No decide prioridades finales (las propone). La implementación de cada propuesta
sería su propio change. Las piezas que tocan **almacenamiento/descarga de documentos** dependen de
[[documental-storage]] / [[reestructura-almacenamiento-documentos]].
