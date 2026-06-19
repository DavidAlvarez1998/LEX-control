# compliance-habeas-data

## Por qué

LEX Control procesa **datos personales** (incluidos datos sensibles: procesos judiciales,
contratos laborales, información financiera) de tres poblaciones distintas. En Colombia esto
obliga a cumplir la **Ley 1581 de 2012** (Habeas Data / protección de datos personales), su
**Decreto reglamentario 1377 de 2013** y la **Circular Externa de la SIC**. Hoy el producto
**no tiene nada de esto**: no hay autorización de tratamiento, ni aviso de privacidad, ni
política publicada, ni términos, ni mecanismo para que un titular ejerza sus derechos. Sin esto
**no se puede vender de forma responsable** (riesgo de sanción de la SIC y de demanda).

> Aclaración legal estructural (define todo el diseño): hay **dos niveles de responsabilidad**.
> - La **plataforma (LEX Control)** es **Responsable** del tratamiento de los datos de: usuarios
>   del despacho (`Usuario`), datos de contacto de la `Empresa`, y prospectos de la propia venta.
> - El **despacho (Empresa)** es **Responsable** de los datos de **sus** clientes y contrapartes
>   (`Cliente`, `Litigante`, partes de un `Proceso`); LEX Control es solo el **Encargado**
>   (procesador) de esos datos por cuenta del despacho.
> Esta distinción exige (a) política/aviso/términos + autorización para los datos de los que la
> plataforma es Responsable, y (b) un **Contrato de Transmisión/Encargo de datos (DPA)** con cada
> despacho + **herramientas** para que el despacho capture la autorización de sus titulares y
> atienda sus derechos.

> Nota: el **texto legal** (política, aviso, términos, DPA) debe ser **revisado y aprobado por un
> abogado colombiano**. Este change define el **modelo de producto y técnico** (qué se captura,
> dónde, cómo se versiona y cómo se ejercen los derechos) + *placeholders* de contenido. No
> sustituye la asesoría jurídica.

## Qué cambia

Capability nueva **`compliance-habeas-data`**. Se implementa por fases (ver `tasks.md`); este
documento + `design.md` + el spec delta son el **plan SDD** previo a implementar.

1. **Documentos legales versionados** (`DocumentoLegal`): Política de Tratamiento de Datos, Aviso
   de Privacidad, Términos y Condiciones, y DPA (encargo despacho↔plataforma). Servidos en rutas
   **públicas** y enlazados en el footer de ambos portales.
2. **Aceptación de términos** (`AceptacionLegal`): al activar la cuenta / primer login, el usuario
   del despacho acepta Términos + Política (versión sellada + fecha + IP como evidencia). El login
   reporta si hay una versión nueva pendiente de aceptar.
3. **Autorización de tratamiento** (`AutorizacionTratamiento`): registro de la autorización previa,
   expresa e informada del titular. Para los datos donde la plataforma es Responsable (usuarios,
   prospectos) y **herramienta para el despacho** (campos de consentimiento al crear/editar
   `Cliente`/`Litigante`: ¿autorizó?, canal, fecha, finalidad) donde es Encargado.
4. **Derechos del titular / PQR de datos** (`SolicitudTitular`): canal y bandeja para consulta,
   reclamo, rectificación, actualización, supresión y revocación, con los **plazos legales**
   (consulta 10 días hábiles +5; reclamo 15 días hábiles +8) y semáforo de vencimiento.
5. **Retención, exportación y supresión**: exportar los datos de un tenant y eliminarlos al
   terminar el servicio (apoyado en el cascade existente de `Empresa`).
6. **Operativo (no software)**: registrar las bases de datos en el **RNBD** de la SIC; designar
   responsable de protección de datos; medidas de seguridad (TLS/cifrado — depende del deploy).

## Impacto

- **Schema** (`lex-control-api`): 4 modelos nuevos (`DocumentoLegal`, `AceptacionLegal`,
  `AutorizacionTratamiento`, `SolicitudTitular`) + enums; campos opcionales de consentimiento en
  `Cliente`/`Litigante`. Aplicar con `db push` (DB no gestionada por migrate).
- **API**: rutas públicas `/publico/legal/*`, gating de aceptación en auth, endpoints de
  autorización y de solicitudes de titular (tenant + admin plataforma).
- **Frontends**: páginas legales públicas + footer; checkbox de aceptación en activación; campos
  de consentimiento en formularios de Cliente/Litigante; sección "Datos personales / Habeas Data".
- **Negocio**: el DPA pasa a ser parte del contrato de servicio con cada despacho.

## Rollback

Cambio **aditivo** y de bajo riesgo: modelos y columnas nuevas (las columnas en `Cliente`/
`Litigante` son opcionales). Rollback = ocultar las rutas/UI nuevas y, si se requiere, hacer
`db push` revirtiendo el schema (no se modifican datos existentes). Los documentos legales son
contenido; despublicarlos no rompe el resto del producto.
