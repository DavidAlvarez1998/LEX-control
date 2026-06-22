# Tasks — unificacion-uploader-documentos

## Componente estándar
- [x] `lex-control-client/src/components/documentos-uploader.tsx` — `DocumentosUploader` con dos modos
      (pendiente: value/onChange; en vivo: existentes/subir/quitar) + `extra`; drag&drop, autocompletar
      nombre, chip con tamaño, reemplazar/quitar, confirmación al quitar (en vivo)
- [x] `lex-control-admin/src/components/documentos-uploader.tsx` — espejo, solo modo en vivo, tokens admin

## Migraciones
- [x] `procesos/nuevo/page.tsx` — "Documentos de prueba" y "Documentos de medidas cautelares" usan el
      estándar (modo pendiente); se eliminó el JSX ad-hoc y los setters por índice
- [x] `adjuntos-libres.tsx` (client) — reescrito como wrapper del estándar (modo en vivo); API pública
      intacta; agrupado por `prefix` conservado
- [x] `documentos-contrato.tsx` (client) — estándar en vivo + categoría como `extra`; `onError` opcional
- [x] `documentos-contrato.tsx` (admin) — idem con primitivas del admin

## No tocados (decisión)
- [x] `BotonSubirDoc` — sigue como estándar de 1 documento fijo
- [x] `DocumentosProceso` — se deja (enlace/URL + plantillas, no sube binarios)
- [x] Backend multer — sin cambios (1 archivo/request)

## Catálogo (ejecutivo mínima cuantía) — relacionado
- [x] `solicitud-cautelares.pdf` → `opcionalesSi` con `si: solicitaCautelares=Sí` + `anclaCampo: otrasCautelares`
- [x] Nuevo soporte `anclaCampo` en `opcionalesSi` (`procesos.ts` + `datos-proceso.tsx`)
- [x] Re-seed catálogo aplicado (33 tipos)

## Gate de verificación
- [x] `tsc --noEmit` verde — client y admin
- [x] `eslint` — archivos nuevos/cambiados limpios (los 2 errores de `nuevo/page.tsx` son preexistentes:
      setState-in-effect)
- [x] `next build` verde — client y admin
- [x] API `vitest` — 485/485 (incluye `seed-tipos.test.ts`); `seed-tipos.json` válido
- [x] Consumidores verificados: `AdjuntosLibres` (datos-proceso.tsx:317), `DocumentosContrato`
      (cuenta:236, contratos:536, admin contratos-comercial:446) — props compatibles
- [ ] Smoke en navegador (subir/quitar real en cada punto) — pendiente con la app corriendo
