# Tasks — reestructura-almacenamiento-documentos

## Verificación previa (proveedor)
- [x] Probado en vivo: tecnovapp solo permite 1 nivel de carpeta (404 al 3er segmento; "/"→"_")
- [x] Confirmado: estructura fija `{EMPRESA}/{CARPETA}/AÑO/MES` + MAYÚSCULA

## Implementación (backend, sin tocar fronts)
- [x] `env.documentos.empresa` (fijo) → `env.documentos.raizPrefijo` (DEMO-LEXCONTROL/LEXCONTROL)
- [x] `documentos.client.ts`: helpers `slugDoc()` + `carpetaTenant()`; `subirDocumento` recibe `raiz`
- [x] `schema.prisma`: `DocumentoProceso` +categoria(enum)+tipo+subidoPorId+índice; `DocumentoContrato` +subidoPorId; `Usuario` back-relations; enum `CategoriaDocumentoProceso`
- [x] `prisma generate`
- [x] `contratos`: repo trae `empresa{id,nombre}`; service usa `carpetaTenant` + carpeta `CONTRATOS` + `subidoPorId`
- [x] `procesos`: repo trae `empresa{id,nombre}`; service usa `carpetaTenant` + carpeta `PROCESOS` + `tipo` + `subidoPorId`
- [x] Tests: `documentos.test.ts` (nueva firma `raiz` + `carpetaTenant`); ajustadas aserciones en `contratos`/`procesos` test

## Gate
- [x] `tsc --noEmit` verde
- [x] `vitest` verde (459 tests, mockeados — sin envíos ni DB real)

## Pendiente
- [ ] **`pnpm push`** — aplica las columnas nuevas a la BD. NO ejecutado: el schema comparte trabajo
      en vuelo del usuario (`Notificacion`, `CategoriaProceso`). Coordinar y pushear cuando ese trabajo esté listo.
- [ ] Auto-clasificar `categoria` al subir (hoy default `OTRO`) — al conectar fronts
