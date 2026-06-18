# form-indentacion-condicional

## Por qué

Los formularios dinámicos de los procesos (sobre todo el laboral, con sus ramas de
admisión, subsanación, reconvención, audiencia…) son **largos** y tienen muchos campos que
**aparecen al elegir una opción** (vía `mostrarSi`). Hoy todos se ven al mismo nivel, así que
cuesta entender **qué campo desprende a cuál** y digitar se vuelve confuso. El usuario lo pidió
explícitamente al ir por el 2.º de 4 casos del laboral.

## Qué cambia

En el renderizador genérico `FormularioDinamico` (que usan **todos** los formularios de proceso,
actuales y futuros), cada campo que aparece por una condición `mostrarSi` se muestra con una
**indentación** proporcional a la **profundidad de su cadena** de `mostrarSi`, con una guía
visual (borde izquierdo). Así:

- Campo sin `mostrarSi` → nivel 0 (sin indentar).
- Campo cuyo `mostrarSi` referencia un campo de nivel N → nivel N+1 (indentado un escalón más).

Es **solo presentación** (no cambia validación, gating ni lógica). Aplica a todos los grupos
(laboral, DdP, tutela, civil…) y a cualquier catálogo que se cree de aquí en más, sin tocar el
seed: la jerarquía se deriva sola de las condiciones que ya existen.

## Impacto

- Código: solo `lex-control-client/src/components/formulario-dinamico.tsx` (cálculo de nivel +
  estilo de indentación en el wrapper de cada campo).
- Sin cambios en API, seed ni motor. Reutiliza `camposDeCondicion`.
