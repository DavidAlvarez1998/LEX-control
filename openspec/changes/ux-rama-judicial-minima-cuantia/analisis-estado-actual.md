# Análisis — estado actual de la UI/UX (mínima cuantía + Rama)

Mapa de lo que el usuario VE y HACE hoy, y dónde hay fricción. Base de las propuestas.

## Pantallas

### 1. Lista de procesos (`/procesos`)
Navegación de 3 niveles: Jurisdicción → Categoría → Tabla. La tabla muestra **Proceso** (título +
tipo · área · código · `Rad. {radicado}`), **Cliente**, **Etapa** (interna), **Vence** (fecha +
semáforo rojo/ámbar/gris), **Responsable**, **Estado** (badge). Filtros: Míos/Todos, búsqueda
(código/título/cliente/radicado), área, estado, responsable. Banner de vencimientos (vencidos +
por vencer). **No muestra nada de novedades de la Rama** ni la última actuación.

### 2. Creación (`/procesos/nuevo?tipo=…`)
Pasos: tipo → cliente (rol) → título (auto "X vs. Y") → **datos judiciales** (radicado con contador
de dígitos en vivo, juzgado manual, cuantía select+monto) → partes → formulario dinámico → documentos
(demanda/poder + cautelares inline si aplica) → responsable. Al guardar un radicado de 23 díg ya
dispara el sync.

### 3. Ficha (`/procesos/[id]`)
- **Card de datos:** código, **radicado editable** (RadicadoDato: contador de dígitos, al guardar
  con 23 díg → sync → juzgado + fecha + actuaciones), estado, cliente, abogado, **despacho/juzgado**,
  cuantía, próxima audiencia (manual), vencimiento (semáforo).
- **Stepper de etapas internas** (Radicación → … → Terminación; ramas/decisiones; bloqueo con campos/
  docs faltantes).
- **Partes**, **Documentos** (adjuntar/generar plantillas), **Formulario dinámico**.
- **Panel "Actuaciones del juzgado"** (lo conectado a la Rama): título + badge "N nuevas", botones
  "Actualizar" / "Marcar como vistas", aviso de sync (nuevas/sin novedades/reservado/no publicado),
  card "Sugerencias de la Rama" (botón "Usar fecha"), y **timeline** (fecha · actuación · anotación)
  con badge "nueva" persistente.

## Gaps / fricciones observadas

| # | Gap | Dónde | Impacto |
|---|---|---|---|
| A | **Sin señal de novedades en la lista** — solo se ven entrando a la ficha | Lista | Alto |
| B | "Próxima audiencia" (manual) vs "Actuaciones" (Rama): el usuario no distingue las fuentes | Ficha | Medio |
| C | **Frescura desconocida**: no hay "última sync hace X" ni "última actuación: fecha" | Ficha | Alto |
| D | Flujo del radicado: contador muy chico (xs); feedback de sync desaparece rápido; falla "en silencio" | Ficha/Crear | Medio |
| E | Documentos: "Pruebas" (nombre libre) vs "cautelares" inline → confuso qué va dónde | Crear/Ficha | Bajo |
| F | "Marcar como vistas" puede leerse como "borrar"; sin confirmación | Ficha | Bajo |
| G | "Sugerencias de la Rama": no se explica de dónde salen (motor de hitos por keywords) | Ficha | Bajo |
| H | Mínima cuantía SIEMPRE es MINIMA, pero el form igual pregunta la cuantía | Crear | Bajo |
| I | No hay **validación en vivo** del radicado contra la Rama mientras se escribe | Ficha/Crear | Medio |
| J | "Próxima audiencia" no se alimenta de las actuaciones (es manual) | Ficha | Medio |
| K | No se puede **descargar/exportar el expediente** ni los documentos del juzgado | Ficha | Alto |
| L | **Dos líneas de tiempo (etapas internas vs actuaciones) se confunden** | Ficha | Alto |
| M | Estado "reservado/no publicado" solo aparece tras "Actualizar"; no es persistente/visible | Ficha | Medio |
| N | "Despacho/juzgado" editable + autollenado: no se ve el **origen** del dato (Rama vs manual) | Ficha | Bajo |

## Capacidades de la API hoy SIN usar (oportunidad — ver [[rama-judicial-actuaciones]] spec)

- **Detalle** (`/Proceso/Detalle/{id}`): tipo/clase/subclase, ponente, **ubicación** ("Secretaría"),
  contenido de radicación, última actualización.
- **Sujetos** (`/Proceso/Sujetos/{id}`): partes ESTRUCTURADAS (Demandante/Demandado + identificación).
- **Documentos** (`/Proceso/Documentos/{id}`) + **Descarga** (`/Descarga/Documento/{idReg}` → **PDF real**).
- **`conDocumentos`** por actuación: enlaza actuación ↔ documentos descargables.
