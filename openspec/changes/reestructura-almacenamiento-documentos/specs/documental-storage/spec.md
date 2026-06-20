# Almacenamiento Documental (delta) — raíz por tenant + metadata

Extiende la spec canónica [[documental-storage]] con el esquema de carpetas multi-tenant (raíz =
despacho, convención del doc §9.1) y la metadata del documento en BD.

## MODIFIED Requirements

### Requirement: La RAÍZ es el tenant y la CARPETA es el módulo
Toda subida usa como RAÍZ `{EMPRESA}` un identificador de tenant y como `{CARPETA}` el módulo. La raíz
se construye con `carpetaTenant(empresa)` = `${env.documentos.raizPrefijo}-${tenant}`, donde `tenant`
es `ADMIN` (plataforma, `empresaId = null`) o `${slug(nombre)}-${empresaId}` (despacho). El servidor
agrega `/{AÑO}/{MES}/{archivo}` y normaliza a MAYÚSCULA. NO se intenta anidar más niveles (tecnovapp
solo acepta un nivel de carpeta: un 3er segmento da 404 y un "/" interno se convierte en "_"). El
prefijo (`env.documentos.raizPrefijo`, p. ej. `DEMO-LEXCONTROL` / `LEXCONTROL`) namespacea el producto
en el tecnovapp compartido y reemplaza al antiguo `env.documentos.empresa` fijo.

#### Scenario: Documento de un despacho
- GIVEN un proceso de la empresa `{id, nombre}`
- WHEN se sube un archivo del proceso
- THEN la raíz es `${raizPrefijo}-${slug(nombre)}-${id}` y la carpeta `PROCESOS`
  → `…/{PREFIJO}-{SLUG}-{ID}/PROCESOS/{AÑO}/{MES}/{archivo}`

#### Scenario: Documento de plataforma (ADMIN)
- GIVEN un recurso de plataforma (`empresaId = null`)
- WHEN se sube un archivo
- THEN la raíz es `${raizPrefijo}-ADMIN` y la carpeta el módulo correspondiente

#### Scenario: Aislamiento por despacho en el almacenamiento
- GIVEN dos despachos distintos
- WHEN cada uno sube documentos
- THEN sus archivos quedan en raíces distintas (no comparten carpeta), además del aislamiento por BD

## ADDED Requirements

### Requirement: Metadata del documento y relaciones por la BD
La fila del documento guarda metadata intrínseca: `categoria` (clase del documento), `tipo` (mime) y
`subidoPorId` (auditoría: quién subió). NO se duplican en el documento los datos del padre
(cliente, juzgado/radicado, abogado, despacho, partes): se alcanzan vía `procesoId`→`Proceso` (o
`contratoId`→`Contrato`). Las consultas ("docs de un proceso/cliente/juzgado/usuario") se resuelven en
la BD, no navegando carpetas.

#### Scenario: Filtrar por clase de documento
- GIVEN documentos de un proceso con distintas `categoria`
- WHEN se piden solo los poderes
- THEN `WHERE procesoId = X AND categoria = PODER`

#### Scenario: Auditoría de subida
- GIVEN un archivo subido por un usuario
- WHEN se consulta el documento
- THEN `subidoPorId` identifica quién lo subió

#### Scenario: Datos del proceso sin denormalizar
- GIVEN un documento de proceso
- WHEN se necesita su cliente o juzgado
- THEN se obtienen por la relación `procesoId`→`Proceso`, sin copiarlos en el documento
