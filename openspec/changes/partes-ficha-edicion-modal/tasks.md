# Tasks

## 1. Mover el form de parte a un Modal (`partes-proceso.tsx`) ✅
- [x] Importar `Modal` de `@/components/ui`.
- [x] Quitar el branching inline `editando === p.id ? formulario : fila` y el
      `editando === "nueva" && <li>{formulario}</li>`: la `<ul>` siempre lista filas.
- [x] Convertir `formulario` en el CUERPO del Modal (campos + error), sin la tarjeta
      indigo ni los botones (el Modal ya es una Card).
- [x] Renderizar `<Modal open={editando !== null} onClose={cancelar} title=… footer=…>`
      con footer = Cancelar + (Agregar | Guardar). `onClose` no cierra mientras `guardando`.
- [x] Simplificar las condiciones del header/empty/helper que dependían de `editando`.

## 2. Verificar
- [x] `tsc` del cliente verde.
- [ ] Manual (lo prueba el usuario): editar → cerrar (X/backdrop/Cancelar); editar A,
      cerrar, editar B sin refrescar; agregar parte; quitar; readOnly sin acciones.
