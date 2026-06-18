# Tasks — laboral-ficha-ux

## Implementación (solo frontend, solo laboral)
- [x] `datos-proceso.tsx`: helper `seccionesLaboral(etapas, esquema)` — agrupa campos por etapa (camposRequeridos + campos de condiciones + dependientes vía mostrarSi, transitivo) en orden; leftover por proximidad
- [x] Rama `grupo === "LABORAL"` de la edición: render por secciones (encabezado + FormularioDinamico subset, una columna) + slots de docs
- [x] `grupo !== "LABORAL"` sin cambios (DdP/tutela intactos)
- [x] La lógica de guardar/validar sigue usando el esquema completo (sin cambios)
- [x] Reubicado `observacionesAdmision` tras `fechaAdmision` en el seed (solo orden de display) + re-seed, para que agrupe en "Calificación"

## Verificación
- [x] `pnpm build` cliente verde
- [x] Simulación de agrupación: 11 secciones en orden del flujo, cada campo en su sección correcta
- [ ] Smoke manual: ficha laboral muestra secciones por etapa, una columna, docs inline; secciones N/A ocultas (única no muestra Contestación; sin inadmisión no muestra Subsanación)

## Cierre
- [ ] Archivar tras smoke + commit
