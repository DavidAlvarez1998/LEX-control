# Tasks — cliente-convert-ownership

## API (lex-control-api)
- [x] `POST /clientes`: `responsableComercialId = req.body.responsableComercialId ?? req.user.sub`
- [x] `GET /clientes` + `GET /clientes/:id`: `include responsableComercial { id, nombre }`
- [x] seed-foundations: `cliente.convertir` += JURIDICO + comentario; re-seed (aditivo)
- [x] test: create auto-asigna responsable = creador (tests/clientes.test.ts)

## Frontend cliente (clientes/page.tsx)
- [x] tipo Cliente: `responsableComercialId` + `responsableComercial { id, nombre }`
- [x] mostrar "Responsable: Fulano" en cada fila
- [x] helper `deOtro(c)`; confirm suave al CONVERTIR el de otro ("Este prospecto es de Fulano…")
- [x] aviso ámbar al EDITAR el de otro (no bloquea)
- [x] detalle `/clientes/[id]`: "Responsable: Fulano (tú)" en la cabecera (tipo + display; usa el GET ya enriquecido)

## Verify
- [x] `pnpm --dir lex-control-api build` (tsc) limpio
- [x] `pnpm --dir lex-control-client build` (next) limpio
- [x] `pnpm --dir lex-control-api test` → 377/377
- [x] re-seed foundations OK (rolEmpresaPermisos 100)
- [x] Smoke en vivo 3/3: JURIDICO no-admin crea (responsable=él) · convierte (200, antes 403) · GET trae responsableComercial.nombre. Limpieza sin residuo
