# API Documental — `documentos.tecnovapp.com.co`

Microservicio genérico de almacenamiento de archivos (estilo Cloudinary). Subes un binario, te devuelve un `path` público. Tú guardas ese `path` en tu BD. Es **independiente** del panel: cualquier app puede usarlo.

> En este sistema (Gestión Social API) reemplaza la decisión pendiente de CLAUDE.md: *"¿Adjuntos en S3 (AWS) o Cloudinary?"* → **se usa este microservicio**. Todos los campos `*_url` del schema (`hoja_vida_url`, `foto_url`, `archivo_url`, `documento_url`, `logo_url`, `notificacion_soporte_url`, etc.) guardarán el `path` o la URL completa que devuelve este servicio.

---

## 0. Lo esencial en 3 frases

1. **Subir** → `POST /api/documento/{EMPRESA}/{CARPETA}` con `multipart/form-data` → responde `{ path, filename, url }`.
2. **Guardar** el `path` en tu BD (en el campo `*_url` del registro correspondiente).
3. **Mostrar** → URL pública = `https://documentos.tecnovapp.com.co/documentos/` + `path`. Sin auth, va directo en `<img>`/`<a>`.

Extra opcional: validar rostro (selfie) y analizar cédula (frente+reverso) sobre un `path` ya subido.

---

## 1. Base URLs

| Entorno | URL |
|---------|-----|
| Producción | `https://documentos.tecnovapp.com.co` |
| Demo | `https://demo-documentos.tecnovapp.com.co` |

Poner en `.env` y validar con Zod (`env.config.ts`):

```
DOCUMENTOS_BASE_URL=https://documentos.tecnovapp.com.co
```

---

## 2. Endpoints

| Acción | Método | Endpoint |
|--------|--------|----------|
| Subir archivo | `POST` | `/api/documento/{EMPRESA}/{CARPETA}` |
| Ver / descargar | `GET` | `/documentos/{EMPRESA}/{CARPETA}/{YYYY}/{MM}/{filename}` |
| Validar rostro | `POST` | `/documentos/validar-rostro` |
| Analizar identidad (cédula) | `POST` | `/documentos/analizar-identidad/completo` |

- `{EMPRESA}` y `{CARPETA}`: strings libres que TÚ decides en la URL. El server crea la carpeta si no existe.
- `{YYYY}` / `{MM}`: los pone el server (fecha del upload).
- `{filename}`: lo decide el server (antepone timestamp para unicidad).

---

## 3. Subir archivo

### Request

```
POST https://documentos.tecnovapp.com.co/api/documento/{EMPRESA}/{CARPETA}
Content-Type: multipart/form-data
```

**Path params** (los inventas tú):

| Param | Ejemplos | Notas |
|-------|----------|-------|
| `{EMPRESA}` | `FINOVA`, `ACME` | Carpeta raíz. |
| `{CARPETA}` | `contratos`, `colaboradores`, `reportes_qr` | Subcarpeta. Server la crea si no existe. |

**Body (form-data):**

| Campo | Tipo | Req | Descripción |
|-------|------|-----|-------------|
| `file` | file | ✅ | Binario (PDF, JPG, PNG, DOC…). |
| `documento` | string | ✅ | Id del dueño (cédula, NIT, id externo). Compone el filename. |
| `tipo` | string | ❌ | Mime type (`image/jpeg`, `application/pdf`). Solo informativo. |

### curl

```bash
curl -X POST 'https://documentos.tecnovapp.com.co/api/documento/MI_EMPRESA/contratos' \
  -F 'file=@/ruta/local/contrato.pdf' \
  -F 'documento=1088327869' \
  -F 'tipo=application/pdf'
```

### Respuesta (200)

```json
{
  "path": "MI_EMPRESA/contratos/2026/06/1717248000000_contrato.pdf",
  "filename": "1717248000000_contrato.pdf",
  "url": "https://documentos.tecnovapp.com.co/documentos/MI_EMPRESA/contratos/2026/06/1717248000000_contrato.pdf"
}
```

- **`path`** → ESTO guardas en BD. Con él reconstruyes la URL siempre.
- **`filename`** → solo el nombre (con timestamp ya antepuesto).
- **`url`** → URL completa lista. **Puede no venir** en algunas versiones; reconstruir desde `path` si falta.

> Distintas versiones del server devuelven distinto nombre de campo. Leer en este orden:
> `resp.data?.url || resp.data?.path || resp.data?.ruta || resp.data?.location`

---

## 4. Ver / descargar

Archivos servidos **estáticos** bajo `/documentos/...`. **Sin auth** = URLs públicas. Van directo en `<img src>` / `<a href>`.

```
GET https://documentos.tecnovapp.com.co/documentos/{path}
```

Ejemplo:
```
https://documentos.tecnovapp.com.co/documentos/MI_EMPRESA/contratos/2026/06/1717248000000_contrato.pdf
```

Helper para reconstruir URL desde el `path` de BD:

```js
function buildUrl(pathFromDB) {
  const BASE = 'https://documentos.tecnovapp.com.co';
  if (!pathFromDB) return null;
  if (/^https?:\/\//i.test(pathFromDB)) return pathFromDB;      // ya es URL absoluta
  if (pathFromDB.startsWith('/')) return `${BASE}${pathFromDB}`; // empieza con /
  return `${BASE}/documentos/${pathFromDB}`;                     // path relativo
}
```

⚠️ **Públicos.** Si necesitas restringir acceso (ej. documentos sensibles, contraseñas de `accesos`), ponlo detrás de TU backend; este servicio no autentica.

---

## 5. Validar rostro (selfie)

Primero subes la foto (punto 3), luego validas que haya un rostro reconocible.

```
POST /documentos/validar-rostro
Content-Type: application/json

{ "path": "FINOVA/CLIENTE/2026/06/1717248000000_foto.jpg" }
```

Éxito:
```json
{ "ok": true, "data": { "landmarks": [ /* ... */ ] } }
```

Rechazo:
```json
{ "ok": false, "data": { "motivo": "MULTIPLES_ROSTROS" } }
```

| Motivo | Significa |
|--------|-----------|
| `SIN_LANDMARKS` | No detecta rostro. |
| `MULTIPLES_ROSTROS` | Más de un rostro. |
| `ROSTRO_NO_CENTRADO` | Rostro no centrado. |

---

## 6. Analizar identidad (cédula)

Cruza frente + reverso del documento, devuelve datos extraídos / coincidencias. Ambos `path` deben venir de uploads previos (punto 3).

```
POST /documentos/analizar-identidad/completo
Content-Type: application/json

{
  "frontalPath": "FINOVA/CLIENTE/2026/06/.../front.jpg",
  "posteriorPath": "FINOVA/CLIENTE/2026/06/.../back.jpg"
}
```

---

## 7. Estructura de almacenamiento

Jerarquía fija a partir de tus params:

```
{EMPRESA}/{CARPETA}/{YYYY}/{MM}/{timestamp}_{nombreOriginal}
```

Ejemplo real:
```
FINOVA/USUARIOS/2026/03/1773508167504_AUTORIZACIONES.pdf
```

Esa ruta = lo que guardas en BD (`path`) y lo que usas para reconstruir la URL pública.

---

## 8. Flujo típico

```
1) POST /api/documento/EMPRESA/CARPETA   (file + documento + tipo)
        ──────────────────────────────►  documentos.tecnovapp
2)      ◄──────────────────────────────  { path, filename, url }
3) Guarda `path` en tu BD junto al registro (colaborador/contrato/etc.)
4) Para mostrar: URL = BASE + "/documentos/" + path
```

---

## 9. Integración en Gestión Social API (NestJS)

### 9.1 Cómo encaja

- **No hay tabla nueva.** El microservicio almacena el binario; tú solo guardas el string `path`/`url` en los campos `*_url` que ya existen en `schema.prisma`.
- **Convención de carpetas multi-tenant:** usar `{EMPRESA}` = slug o id de la empresa (`empresa_id`) para aislar archivos por tenant. `{CARPETA}` = el submódulo (`colaboradores`, `contratos`, `dotaciones`, `reportes_qr`, `certificaciones`, `documentos_contrato`).
  - Ej: `POST /api/documento/empresa-3/contratos`
- **`documento`** (campo form-data) = `numero_documento` del colaborador o id lógico del dueño.

### 9.2 Módulo recomendado: `common/storage` o `modules/documentos`

Servicio inyectable que centraliza el upload. Esqueleto:

```typescript
// src/common/storage/storage.service.ts
import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

interface UploadResult {
  path: string;
  filename?: string;
  url: string;
}

@Injectable()
export class StorageService {
  private readonly baseUrl: string;

  constructor(private config: ConfigService) {
    this.baseUrl = this.config.getOrThrow<string>('DOCUMENTOS_BASE_URL');
  }

  /**
   * Sube un archivo al microservicio documental.
   * @param empresa  carpeta raíz (ej. slug/id de la empresa — tenancy)
   * @param carpeta  submódulo (contratos, colaboradores, reportes_qr…)
   * @param file     buffer del archivo (Express.Multer.File)
   * @param documento id del dueño (numero_documento / id lógico)
   */
  async subir(
    empresa: string,
    carpeta: string,
    file: Express.Multer.File,
    documento: string,
  ): Promise<UploadResult> {
    const form = new FormData();
    const blob = new Blob([file.buffer], { type: file.mimetype });
    form.append('file', blob, file.originalname);
    form.append('documento', documento);
    form.append('tipo', file.mimetype);

    const res = await fetch(
      `${this.baseUrl}/api/documento/${encodeURIComponent(empresa)}/${encodeURIComponent(carpeta)}`,
      { method: 'POST', body: form },
    );

    if (!res.ok) {
      throw new InternalServerErrorException('Fallo al subir documento');
    }

    const data: any = await res.json();
    // distintas versiones devuelven distinto campo
    const path = data?.path ?? data?.ruta ?? null;
    const url =
      data?.url ?? data?.location ?? (path ? this.buildUrl(path) : null);

    if (!path && !url) {
      throw new InternalServerErrorException('Respuesta inesperada del documental');
    }

    return { path: path ?? url, filename: data?.filename, url };
  }

  buildUrl(pathFromDB: string | null): string | null {
    if (!pathFromDB) return null;
    if (/^https?:\/\//i.test(pathFromDB)) return pathFromDB;
    if (pathFromDB.startsWith('/')) return `${this.baseUrl}${pathFromDB}`;
    return `${this.baseUrl}/documentos/${pathFromDB}`;
  }
}
```

> Registrar `StorageService` en un módulo `@Global()` (como `ModulosModule`) para inyectarlo en cualquier servicio sin re-importar.

### 9.3 Qué guardar en BD

**Guardar el `path`** (relativo), no la URL completa. Razón: si cambia el dominio (prod → demo, migración), reconstruyes con `buildUrl()` y no rompes registros viejos.

| Campo schema | Carpeta sugerida |
|--------------|------------------|
| `colaboradores.foto_url` | `colaboradores` (validar rostro) |
| `colaboradores.hoja_vida_url` | `colaboradores` |
| `certificaciones_colaborador.archivo_url` | `certificaciones` |
| `documentos_colaborador.archivo_url` | `documentos` |
| `dotaciones_colaborador.archivo_url` | `dotaciones` |
| `documentos_contrato.archivo_url` | `documentos_contrato` |
| `contratos.notificacion_soporte_url` | `contratos` |
| `reportes_colaborador.archivo_url` | `reportes_qr` |
| `incapacidades.archivo_url` | `incapacidades` |
| `solicitudes_*.archivo_soporte_url` / `documento_url` | `permisos` / `vacaciones` |
| `registros_disciplinario.documento_url` | `disciplinario` |
| `perfiles_empresa.logo_url` | `empresa` |

### 9.4 Tenancy + seguridad

- **Tenancy:** `{EMPRESA}` en la ruta de upload = `empresa.slug` o `empresa_id` del `CreadorCtx`. Mantiene aislamiento de archivos por tenant (igual que `WHERE empresa_id`).
- **Archivos públicos:** las URLs `/documentos/...` no autentican. NO subir ahí nada secreto que no deba ser adivinable. Para credenciales del módulo `Accesos`, no usar este servicio.
- **Controller:** usar `@UseInterceptors(FileInterceptor('file'))` (Multer, `memoryStorage`) para recibir el binario, luego pasar `file.buffer` a `StorageService.subir()`.

### 9.5 Casos especiales

- **Foto colaborador / selfie:** subir → `POST /documentos/validar-rostro` con el `path`. Si `ok=false`, rechazar y devolver el `motivo` al cliente.
- **Onboarding con cédula:** subir frente + reverso → `POST /documentos/analizar-identidad/completo`. Útil para autollenar `numero_documento`, `nombres`, etc. en alta de colaborador.

---

## 10. Cheatsheet (frontend / cliente)

```js
// === Subir ===
const fd = new FormData();
fd.append('file', archivo);          // binario
fd.append('documento', '1088327869'); // id del dueño
fd.append('tipo', 'application/pdf'); // opcional

const r = await fetch(
  'https://documentos.tecnovapp.com.co/api/documento/MI_EMPRESA/contratos',
  { method: 'POST', body: fd },
).then(r => r.json());

// r.path → guardar en DB
// r.url  → mostrar (o reconstruir desde path)

// === Ver ===
const url = `https://documentos.tecnovapp.com.co/documentos/${pathGuardado}`;
// <img src={url}> / <a href={url}>
```

### Reglas que no romper

- `{CARPETA}` la decides tú, va en la URL, server la crea si no existe.
- El `filename` final lo decide el server (timestamp antepuesto). Guarda lo que devuelve.
- Archivos públicos vía `/documentos/...`. Restricción de acceso = tu backend.
- Tamaño máx lo limita el server (consultar a tecnovapp para archivos grandes).
