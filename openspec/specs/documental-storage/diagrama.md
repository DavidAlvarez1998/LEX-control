# Almacenamiento Documental — Diagramas

> Compañero visual del spec canónico [`spec.md`](./spec.md). El binario vive en un
> microservicio EXTERNO (tecnovapp); en nuestra BD guardamos únicamente la `path`
> relativa, y la URL pública se RECONSTRUYE al leer. Referencia de implementación:
> `lex-control-api/src/modules/documentos/documentos.client.ts`.

## 1. El principio: el binario NO vive con nosotros

```mermaid
flowchart TB
    subgraph FE["🖥️ Frontend"]
        U["Usuario sube archivo"]
    end

    subgraph API["⚙️ API @lex (Express)"]
        EP["Endpoint multipart<br/>multer en memoria · 15 MB<br/>requireAuth + requirePermiso"]
        CL["documentos.client.ts<br/>subirDocumento()"]
        RD["construirUrlDocumento(path)<br/>al LEER"]
    end

    subgraph TV["☁️ tecnovapp (microservicio EXTERNO)"]
        BIN["📦 Aquí vive el BINARIO de verdad<br/>1 solo nivel de carpeta libre"]
    end

    subgraph DB["🗄️ Nuestra BD (MySQL)"]
        ROW["fila DocumentoProceso<br/>guarda SOLO la path (string)<br/>nunca el binario · nunca la URL absoluta"]
    end

    U -->|"1 · multipart"| EP
    EP -->|"2 · subirDocumento(...)"| CL
    CL -->|"3 · POST archivo"| BIN
    BIN -->|"4 · { path, filename, url }"| CL
    CL -->|"5 · guarda path"| ROW
    ROW -.->|"al leer: path"| RD
    RD -.->|"URL pública<br/>(dominio reconstruido)"| FE
```

Si cambia el dominio (DEMO → producción) los registros NO se tocan: solo cambia
`env.documentos.apiUrl` y `construirUrlDocumento` reconstruye contra el nuevo dominio.

## 2. Estructura de la carpeta en tecnovapp

tecnovapp solo permite **UN nivel de carpeta libre**. El server agrega AÑO/MES y pasa
a MAYÚSCULA.

```mermaid
flowchart LR
    R["RAÍZ paraguas<br/><b>DEMO-LEXCONTROL</b><br/>env.raizPrefijo"]
    C["CARPETA = tenant_MÓDULO<br/><b>BUFETE-PEREZ-CL9A_PROCESOS</b><br/>carpetaModulo(empresa, modulo)"]
    Y["AÑO<br/><b>2026</b>"]
    M["MES<br/><b>06</b>"]
    F["ARCHIVO<br/><b>1781..._poder.pdf</b>"]

    R --> C --> Y --> M --> F

    C -. "el server agrega" .-> Y
    note["slug del nombre + empresaId<br/>= aísla cada despacho<br/>(ADMIN si es plataforma)"]
    C --- note
```

Forma de la `path`: `{raizPrefijo}/{slug}-{empresaId}_{MÓDULO}/{YYYY}/{MM}/{filename}`

Ejemplos reales:

```
DEMO-LEXCONTROL / BUFETE-PEREZ-CL9A_PROCESOS  / 2026 / 06 / 1781..._poder.pdf
DEMO-LEXCONTROL / ADMIN_USUARIOS              / 2026 / 06 / 1781..._foto.jpg
DEMO-LEXCONTROL / BUFETE-PEREZ-CL9A_CONTRATOS / 2026 / 06 / 1781..._contrato.pdf
```

Claves del diseño:
- **Una sola raíz paraguas** por producto (`DEMO-LEXCONTROL` / `LEXCONTROL`).
- El **tenant va en el nombre de la carpeta** (`{slug}-{empresaId}`), no en un subnivel.
- El **detalle (qué proceso, cliente, juzgado) NO se modela en carpetas** — vive en la BD.

## 3. La fila en la BD y los 4 tipos que conviven

`DocumentoProceso` → tabla `documentos_tramite`.

```mermaid
flowchart TB
    subgraph Tabla["DocumentoProceso → tabla documentos_tramite"]
        direction TB
        F1["procesoId → Proceso (cliente/juzgado/partes salen de aquí)"]
        F2["categoria: DEMANDA·PODER·PRUEBA·ANEXO·AUTO·SENTENCIA·IMPUGNACION·GENERADO·OTRO"]
        F3["nombre: 'poder.pdf' (el gating de etapa es por nombre)"]
        F4["url: path tecnovapp | enlace absoluto | null"]
        F5["contenido: borrador de plantilla (Text) | null"]
        F6["tipo: mime · subidoPorId: auditoría · origenRamaIdReg: idempotencia CPNU"]
    end

    subgraph Tipos["4 tipos en la MISMA tabla"]
        direction TB
        T1["📤 Subido → url = path · contenido = null"]
        T2["🔗 Por enlace → url = URL absoluta"]
        T3["📝 Generado → url = null · contenido = HTML (categoria GENERADO)"]
        T4["⚖️ Importado de la Rama → url = path · origenRamaIdReg evita duplicar"]
    end

    Tabla --> Tipos
```

## 4. Las dos reglas que lo sostienen

1. **Ningún módulo hace `fetch` directo a tecnovapp.** Todo pasa por
   `documentos.client.ts` (`subirDocumento` / `construirUrlDocumento`). Cambiar de
   proveedor o entorno = tocar solo `env.documentos`.
2. **Sin denormalizar.** El documento no copia datos del padre: "los poderes de este
   proceso" = `WHERE procesoId = X AND categoria = PODER` en la BD, no navegar carpetas.

El mismo patrón es **canónico y transversal**: `DocumentoContrato` (tabla
`documentos_contrato`) lo sigue igual, con su carpeta `{tenant}_CONTRATOS` y su columna `path`.
