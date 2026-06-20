# reestructura-almacenamiento-documentos

## Por qué

Hoy TODOS los archivos de la plataforma caen en `demo-lex-control/CONTRATOS/…` y `…/PROCESOS/…`,
**sin aislamiento por despacho** en las carpetas (la separación por tenant existía solo en la BD).
Se reestructura el guardado en tecnovapp para que cada despacho tenga su propio espacio y la
plataforma el suyo (`ADMIN`), siguiendo la convención multi-tenant que recomienda el propio doc del
proveedor (`roadmap-docs/APIs/API-DOCUMENTOS-INTEGRACION (1).md`, §9.1: `{EMPRESA}` = tenant,
`{CARPETA}` = módulo). Además se enriquece la metadata del documento en la BD para consultas futuras.

## Hallazgo verificado (límite duro de tecnovapp)

Pruebas en vivo contra el proveedor confirmaron que **solo permite UN nivel de carpeta**:
- 3er segmento en la URL → **404**; "/" dentro de la carpeta → lo convierte en "_"; el `documento` y el
  nombre de archivo con "/" → ignorados/recortados.
- La estructura es **fija**: `{EMPRESA}/{CARPETA}/{AÑO}/{MES}/{archivo}` (el server agrega AÑO/MES y
  pasa todo a MAYÚSCULA).

Conclusión: no se puede anidar `EMPRESA/MODULO/…`. Se usa la **raíz como tenant** y la **carpeta como
módulo** (lo que el doc recomienda), namespaceado por producto/entorno.

## Qué cambia

### Almacenamiento (tecnovapp) — raíz paraguas única (estilo doc §7)
```
{PREFIJO} / {TENANT}_{MÓDULO} / AÑO / MES / archivo
raíz {EMPRESA}     {CARPETA}      (server)
```
- `PREFIJO` = `env.documentos.raizPrefijo` (`DEMO-LEXCONTROL` demo · `LEXCONTROL` prod) — **única raíz**
  del producto; mantiene limpia la raíz de tecnovapp (compartida). Reemplaza al antiguo
  `env.documentos.empresa`. (Decisión: paraguas §7 en vez de raíz-por-tenant §9.1, porque el equipo
  ya trabajaba bajo una sola carpeta y evita N carpetas en la raíz compartida.)
- `{CARPETA}` = `carpetaModulo(empresa, modulo)` = `{TENANT}_{MÓDULO}` (único nivel libre).
- `TENANT` = `ADMIN` (plataforma) · `{slug-nombre}-{empresaId}` (despacho).
- `MÓDULO` = `CONTRATOS` · `PROCESOS` · (futuros: `EMPRESAS`, `USUARIOS`, `CLIENTES`, `FACTURACION`).
- El id de la entidad (código de proceso / cédula) sigue en `documento` → nombre del archivo.

### BD (metadata + relaciones)
- `DocumentoProceso`: + `categoria` (enum `CategoriaDocumentoProceso`, default `OTRO`), + `tipo` (mime),
  + `subidoPorId` (Usuario, auditoría) + índice por `categoria`.
- `DocumentoContrato`: + `subidoPorId`.
- `Usuario`: back-relations de auditoría.
- **No se duplica** cliente/juzgado/abogado/despacho en el documento: se alcanzan vía `procesoId` →
  `Proceso` (clienteId, responsableId, empresaId, radicado, partes…). Las consultas viven en la BD.

## Cumple la API del proveedor

Respeta al 100% el contrato de tecnovapp (estructura fija, raíz=tenant §9.1, carpeta=módulo, guardar
solo el `path`). La metadata nueva es 100% nuestra (BD), invisible al proveedor. Ver
[[convencion-integraciones-externas]] y la spec canónica [[documental-storage]].

## Migración

- Lo existente (`CONTRATOS/…`, `PROCESOS/…` sin tenant) **se queda** (data demo; tecnovapp no tiene
  borrar/mover). El esquema nuevo rige de aquí en adelante. Los `path` viejos siguen resolviéndose
  (se guarda el path completo en BD).
- **`pnpm push` PENDIENTE**: el schema comparte cambios en vuelo del usuario (`Notificacion`,
  `CategoriaProceso`). No se ejecutó push para no aplicar esos modelos prematuramente. El gate
  (tsc + 459 tests, mockeados) pasa sin push.

## Fuera de alcance

Frontends (no se tocan). Auto-clasificar `categoria` por el flujo de subida (hoy queda `OTRO`;
se afina al conectar los fronts). Módulos `CLIENTES`/`FACTURACION` (cuando existan).
