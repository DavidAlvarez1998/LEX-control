# Plan — Derecho de Petición (enviado y recibido)

> SDD por caso · paraguas: [proposal.md](proposal.md) · doc fuente:
> `roadmap-docs/DERECHO DE PETICIÓN - JUAN DAVID.docx`
> análisis previo: `openspec/changes/flujos-constitucional-peticion/{fuente-juan-david.txt,comparacion,proposal}.md`

## Estado actual (verificado en seed-tipos.json)

- **DdP enviado**: 18 campos, 6 etapas (`borrador → radicada → respondida → {reiteracion |
  escala_tutela} → terminada`). Cliente = peticionario.
- **DdP recibido**: 14 campos, 5 etapas (`recepcion → contestacion → {reiteracion |
  escala_tutela} → terminada`). Cliente = entidad receptora (el plazo corre en contra).
- Motor de **días hábiles** (CO) ya operativo: `plazoDiasPorValorDe` mapea el plazo según
  `tipoPeticion` (General 15 / Documental 10 / Consulta 30). Documentos anclados; escala a
  tutela vía `crearDerivado` (proceso aparte enlazado por caso).
- Genera 1 plantilla (`RESPUESTA_DDP_RECIBIDO`).

## Problemas del doc (a reconciliar)

1. **Doc muy repetido**: el bloque "enviado" y el "recibido" son casi idénticos y repiten la
   sección RECURSO→tutela→(demanda/pruebas/anexos). Ya se resolvió separando en dos tipos +
   `crearDerivado`; **no replicar** el sub-flujo de tutela embebido.
2. **Nomenclatura confusa**: `fechaRadicado` vs. "Nro de radicado"; "Envío físico/correo"
   sin definir si es select/multiselect. Revisar contra el esquema y dejar una sola forma.

## Brechas vs. mínima cuantía

- **API externa**: **la Rama NO aplica** (DdP no es judicial; no hay radicado CPNU).
- Plazos días hábiles, etapas condicionales y derivación: **en paridad**.
- Posible mejora (no Rama): **notificación de vencimiento** del término de respuesta usando
  el módulo `notificaciones` (correo SES / SMS) — recordatorio al abogado X días hábiles
  antes de `fechaLimite`. Es realista porque el motor de vencimientos ya existe. **Opcional**
  y a confirmar; no es requisito de "paridad de flujo".

## Tareas

1. **Confirmar**: para DdP el "consumo de API" es **notificaciones de vencimiento**, no la
   Rama. ¿Se incluye en este alcance o se difiere?
2. Si se incluye: trigger (cron o endpoint `vencimientos?grupo=PETICION`) → `enviarCorreo`
   al responsable con radicado/entidad/días restantes. Reusar `notificaciones`.
3. **Limpiar nomenclatura** del radicado/medio de envío (una sola forma).
4. **Revisar** que `escala_tutela` copie sustancia suficiente (entidad, tipoPeticion,
   queSolicita / peticionario) a la tutela derivada.
5. Smoke: flujo enviado (radica → responde Sí/Parcial/No → termina) y derivación a tutela.
