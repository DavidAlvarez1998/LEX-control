# Public Landing Specification (delta)

> El change `cuenta-autoservicio-empresa` **rediseña el formulario "Crea tu cuenta"**: cambia los
> campos a los pedidos (despacho/abogado + datos del usuario), quita el selector de plan (el plan es
> trial automático) y cambia el mensaje de éxito (de "te revisaremos" a "revisa tu correo para
> activar"). El resto de la landing (hero, módulos, planes informativos, footer) no cambia.

## MODIFIED Requirements

### Requirement: Create-account form (despacho + admin + plan)

**Reemplazada por →**

### Requirement: Create-account form (alta autoservicio)
La landing MUST incluir un formulario **"Crea tu cuenta"** (sección `#cuenta`) que aprovisiona el
despacho de inmediato. Campos (con estos labels): **Despacho / abogado** [req] → nombre del despacho;
**Nit/cc** [req]; **Tarjeta profesional** [opcional]; **Correo** [req, será su login];
**Teléfono notificación personal** [req]; **Nombre usuario** [req]; más un honeypot oculto
(`website`). MUST hacer `POST /publico/solicitud-cuenta`. **No** lleva selector de plan (la cuenta
nace en el plan trial por defecto). En éxito MUST mostrar una confirmación que indique que **se
envió un correo con el link para activar la cuenta** y empezar a trabajar el despacho; en error de
validación MUST mostrar el mensaje sin limpiar los inputs; en 409 (correo o NIT ya registrado) MUST
mostrar un mensaje claro; MUST NOT bloquear la página ante el fallo. Bajo el formulario sigue el
link "¿Ya tienes cuenta? Ingresar" → `/login`.

#### Scenario: Alta exitosa
- **GIVEN** un visitante que completa Despacho/abogado, Nit/cc, Correo, Teléfono y Nombre usuario
- **WHEN** envía el formulario
- **THEN** se llama `POST /publico/solicitud-cuenta` y ve una confirmación del tipo
  "Listo, revisa tu correo para activar tu cuenta y entrar a tu despacho"

#### Scenario: Correo o NIT ya registrado
- **GIVEN** el correo o el NIT ya existen en la plataforma
- **WHEN** el visitante envía el formulario
- **THEN** ve un mensaje claro ("ya existe una cuenta con ese correo" / "ese NIT/CC ya está
  registrado") sin perder lo que escribió

#### Scenario: Feedback de validación
- **GIVEN** el correo está malformado o falta un campo requerido
- **WHEN** se envía el formulario
- **THEN** se muestra el mensaje de validación y no se limpian los inputs

#### Scenario: Sin selector de plan
- **GIVEN** la sección "Crea tu cuenta"
- **WHEN** se renderiza el formulario
- **THEN** no hay selector de plan (la cuenta nace trial); los planes solo se muestran como
  información en la sección de precios
