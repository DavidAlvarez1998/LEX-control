# Editar partes en la ficha: del form inline a un Modal

## Problema

En la ficha del proceso, el panel **Partes** (columna derecha, 1/3 del ancho) edita y
agrega partes con un formulario **inline** que reemplaza la fila de la parte
(`partes-proceso.tsx`). En esa columna estrecha el form es alto y genera fricción:

- Al darle **"editar"** el form se despliega y empuja el resto; el botón **Cancelar**
  queda abajo, lejos del "editar" que se tocó → cuesta encontrar cómo **contraerlo**.
- Para **editar otra parte** hay que cerrar la actual primero; como el form ocupa la
  fila y es largo, en la práctica **tapa** la lista y el usuario termina **refrescando
  la página** para poder editar a otra.

## Propuesta

Mover el formulario de **agregar/editar parte** a un **`Modal`** (el componente
canónico `ui.tsx` → `Modal`, ya portaleado a `<body>` por el bug de Firefox y con
scroll propio). La lista de partes queda siempre como **filas limpias** (nombre, rol,
acciones `editar`/`quitar` + `+ Agregar parte`).

Beneficios, atados 1:1 a las quejas:
- **Contraer**: el Modal cierra con la X / backdrop / Cancelar — afford­ance claro.
- **No tapa la lista**: el form es un overlay; la lista permanece intacta detrás.
- **Editar otra**: cerrar el Modal y tocar "editar" en otra parte lo reabre con sus
  datos; sin refrescar.

Cambio acotado a `partes-proceso.tsx`. Sin tocar backend, modelo ni los endpoints
(`agregarParte`/`editarParte`/`eliminarParte`). Sin librerías nuevas.

## Alcance

- Solo `lex-control-client/src/components/partes-proceso.tsx`.
- Reusa `Modal` (`open`, `onClose`, `title`, `footer`, `size`). Footer = Cancelar +
  Agregar/Guardar; el error y los campos van en el cuerpo.
- Se conserva el modelo de estado actual (`editando` = id | "nueva" | null); el Modal
  abre cuando `editando !== null`.
