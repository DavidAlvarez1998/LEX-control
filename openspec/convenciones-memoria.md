# Convención de memoria / conocimiento del proyecto

> Cómo se guarda el conocimiento de este proyecto para que sea **escalable** y **durable**.
> Definido con el usuario el 2026-06-20.

## Regla base

Cuando el usuario dice **"guarda en memoria"** → se escribe en **openspec** (en el
repo, durable, versionado y compartible con el equipo). El resto son apoyos.

## Las 3 capas (de más durable a menos)

| Capa | Persiste | En el repo | Para qué |
|---|---|---|---|
| **openspec/** | Siempre (git) | ✅ Sí | **Fuente de verdad.** Decisiones, diseño, specs, hallazgos durables. |
| **Memoria de archivos** (`~/.claude/projects/.../memory/`) | Sí, se carga cada sesión | ❌ No | Notas rápidas de contexto del asistente. |
| **engram** (MCP) | Sí (store externo) | ❌ No | Apoyo; recall por búsqueda, puede "no aparecer". |

## Cómo escala cada capa

**openspec/** (lo importante):
- `changes/<nombre>/` — propuestas/diseños/análisis por feature (proposal.md, etc.).
- `specs/` — specs canónicas ya archivadas.
- `roadmap-docs/` — documentos fuente del cliente (.docx/.odt).
- Crece por carpetas; sin límite de tamaño que afecte al contexto.

**Memoria de archivos** — patrón **router + detalle**:
- `MEMORY.md` = **índice liviano**, agrupado por tema, **1 línea corta por memoria**
  (es el ÚNICO archivo que el harness carga automáticamente cada sesión → debe
  quedar chico, hoy ~13 KB de ~24 KB de límite).
- `<tema>.md` = **un archivo por tema** con el detalle (con fecha en el cuerpo). Se
  leen **a demanda**, no pesan en el contexto. Aquí vive el volumen → escala acá.
- NO sirve tener "varios MEMORY.md": el harness solo lee el de la ruta fija.

## Reglas prácticas

1. Decisión/diseño/hallazgo durable → **openspec** (y opcional un pointer en la
   memoria de archivos).
2. `MEMORY.md`: entradas de 1 línea (~≤200 chars). El detalle va en el `<tema>.md`.
3. Si `MEMORY.md` se acerca al límite → **compactar** (acortar renglones), no crear
   más índices.
4. engram: úsalo como apoyo, no como fuente única (se pierde entre sesiones).
