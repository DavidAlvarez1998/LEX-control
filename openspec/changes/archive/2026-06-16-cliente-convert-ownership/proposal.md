# Proposal: Convertir prospecto (abogado incluido) + responsable visible, sin muro

## Problema reportado
Un usuario reportó que "si un prospecto es de un usuario y otro lo va a pasar a cliente, no deja", y
pidió validar la regla de la vida real (¿un abogado/comercial puede convertir/editar el prospecto-
cliente de otro?). La realidad técnica era distinta a lo percibido:

1. **No existe ningún muro de pertenencia.** El API de clientes solo filtra por `empresaId` + rol.
   Cualquiera del despacho con el rol adecuado podía editar/convertir cualquier cliente. No había
   bloqueo "es de fulano".
2. **`responsableComercialId` casi siempre estaba vacío**: al crear un prospecto NO se asignaba
   responsable → los prospectos no "pertenecían" a nadie en los datos.
3. **El "no deja" era RBAC, no pertenencia**: `cliente.convertir` lo tenían solo ADMINISTRADOR +
   COMERCIAL. Un abogado (JURIDICO) NO podía convertir → recibía un `403 "No autorizado"` genérico,
   que se interpretó como "le pertenece a otro".

## Decisión (validada contra la práctica de bufetes — estándar Clio/MyCase)
En un bufete NO se ponen muros de pertenencia sobre clientes (cobertura cuando alguien falta + chequeo
de conflictos de interés sobre toda la cartera). La pertenencia sirve para **atribución y
responsabilidad**, no para bloquear. Por eso:

- **`cliente.convertir` ahora incluye JURIDICO** (ADMINISTRADOR + COMERCIAL + JURIDICO): el abogado que
  hace el intake puede activar su propio prospecto sin depender de un comercial.
- **Sin muro de pertenencia** (se mantiene): cualquiera con el rol puede editar/convertir; se AVISA de
  quién es, no se bloquea.
- **El responsable se asigna automáticamente al crear** (= el creador, salvo que el admin fije otro en
  el body) → ahora los prospectos sí tienen dueño para atribución y para el filtro "Míos".
- El "responsable" pasa a ser el **originador** (puede ser JURIDICO o COMERCIAL); se relaja la guía
  blanda "SHOULD hold COMERCIAL" (nunca estuvo enforced en código).

## Scope
- **API** (clientes.router.ts): `POST /clientes` asigna `responsableComercialId = body ?? req.user.sub`;
  `GET /clientes` y `GET /clientes/:id` incluyen `responsableComercial { id, nombre }`.
- **RBAC** (seed-foundations.ts): `cliente.convertir` += JURIDICO. Re-seed (aditivo, upsert).
- **Frontend cliente** (clientes/page.tsx): muestra "Responsable: Fulano" en la lista; confirm suave al
  CONVERTIR el de otro ("Este prospecto es de Fulano…"); aviso ámbar al EDITAR el de otro. Sin bloqueo.

## Out of scope
- Renombrar la columna `responsableComercialId` (sigue igual; solo cambia su semántica a "originador").
- Muro/atribución de comisión por pertenencia (la comisión ya se maneja aparte).

## Rollback
Aditivo. Revertir = quitar JURIDICO de `cliente.convertir` (re-seed), quitar el auto-responsable y los
avisos del front. Datos: los `responsableComercialId` ya asignados quedan (inocuos).
