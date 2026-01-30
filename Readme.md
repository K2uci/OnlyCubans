# Reporte de Vulnerabilidades - API Orquestador Evertec

**Fecha del Informe:** 30 de Enero de 2026
**Autor:** Agente de Ciberseguridad Gemini

## Resumen Ejecutivo

Durante la evaluación de seguridad de la API "Orquestador Evertec", se han identificado varias vulnerabilidades, entre las que destaca una **falla crítica de control de acceso a nivel de API**. Todo un controlador, que gestiona operaciones sensibles sobre tarjetas y datos de clientes, se encuentra completamente desprotegido, permitiendo que cualquier persona en Internet pueda leer y modificar datos sin ningún tipo de autenticación.

Adicionalmente, se ha detectado que la documentación proporcionada para la autenticación de uno de los controladores es incorrecta, impidiendo el uso legítimo de dicha funcionalidad.

A continuación, se detallan los hallazgos.

---

## Listado de Hallazgos

### 1. [CRÍTICO] Falla de Autenticación en el Controlador de Tarjeta de Débito

- **Severidad:** **CRÍTICA**
- **CWSS:** 9.8 (Acceso No Autenticado a Funcionalidad Crítica)
- **Descripción:** La totalidad de los endpoints bajo el controlador `/TarjetaDebito` no implementan ningún tipo de validación de autenticación. Esto permite que un atacante anónimo pueda invocar directamente funcionalidades sensibles que deberían estar protegidas, como la consulta de datos de tarjetas, la actualización de datos de clientes y la modificación del estado de las tarjetas. La API procesa las peticiones y las pasa a la lógica de negocio, en lugar de rechazarlas con un error `401 Unauthorized`.
- **Impacto:** Un atacante puede leer información sensible de tarjetas (potencialmente el PAN completo), modificar datos personales de los clientes (email, teléfono), y alterar el estado de las tarjetas (bloquear, cancelar), causando un impacto directo en la confidencialidad, integridad y disponibilidad de los datos de los clientes.
- **Endpoints Afectados:**
    - `GET /TarjetaDebito/ObtenerInfoTarjetaPorNumeroTarjeta`
    - `POST /TarjetaDebito/ActualizarDatosCliente`
    - `POST /TarjetaDebito/ActualizarEstado`
    - `POST /TarjetaDebito/ExcepcionesDeCompras`
- **Prueba de Concepto (PoC):**
  Se realiza una petición al endpoint `ActualizarDatosCliente` sin el encabezado `Authorization`. La API responde con un `200 OK` y un error de negocio, en lugar de un `401 Unauthorized`.

  ```bash
  curl -s -i -X POST \
    -H "Content-Type: application/json" \
    -d '{"NumeroCuentaPayStudio":"1234567890", ...}' \
    "https://apim-transversal-dev.azure-api.net/orquestadorevertec/TarjetaDebito/ActualizarDatosCliente"
  ```
  **Respuesta del Servidor:**
  ```http
  HTTP/1.1 200 OK
  ...
  {"Success":false,"Error":"El motor de evertec ha devuelto los siguientes errores [{\"ErrorCode\":\"ICS0178\",\"ErrorText\":\"El cliente con documento 0987654321 y tipo de documento 13 no existe\"}]"}
  ```
- **Recomendación:** Aplicar de forma mandatoria el middleware de autenticación y autorización (validación de token OAuth2) a nivel del controlador `/TarjetaDebito` y a cada uno de sus endpoints. Toda petición que no contenga un token válido debe ser rechazada con un código de estado `401 Unauthorized`.

---


### 2. [ALTO] Referencia Insegura y Directa a Objetos (IDOR) sin Autenticación

- **Severidad:** **ALTA** (Considerada Crítica en combinación con el hallazgo #1)
- **CWSS:** 9.1 (Modificación no Autorizada de Datos)
- **Descripción:** Como consecuencia directa de la falta de autenticación en el controlador `/TarjetaDebito`, no existe ningún mecanismo que valide que el "dueño" del token (en un escenario normal) esté autorizado para acceder o modificar los datos referenciados. Cualquier atacante puede enviar identificadores (`NumeroDocumento`, `TrackingId`) de cualquier cliente o tarjeta y la API intentará procesar la petición.
- **Impacto:** Permite a un atacante modificar o leer datos de cualquier usuario del sistema, no solo los propios. Un atacante podría, por ejemplo, bloquear la tarjeta de otro usuario o cambiar sus límites de compra.
- **Endpoints Afectados:** Todos los endpoints del controlador `/TarjetaDebito`.
- **Prueba de Concepto (PoC):** La misma PoC del hallazgo #1 demuestra que se puede intentar operar sobre cualquier objeto (`NumeroDocumento: "0987654321"`) sin necesidad de probar la propiedad sobre dicho objeto.
- **Recomendación:** Además de implementar la autenticación (hallazgo #1), es crucial que la lógica de negocio valide que el `appid` o el `oid` (Object ID) del token de acceso tiene los permisos necesarios para operar sobre el recurso solicitado (la cuenta, la tarjeta, etc.). Por ejemplo, una petición para modificar la tarjeta con `TrackingId: "XYZ"` debe ser validada para asegurar que el dueño del token está asociado a esa tarjeta.

---


### 3. [BAJO] Documentación de Autenticación Incorrecta

- **Severidad:** **BAJA**
- **CWSS:** 3.1 (Degradación de la Funcionalidad)
- **Descripción:** La documentación de la API detalla un método para obtener un token de acceso para la API (mediante `client_id` y `client_secret`). Sin embargo, el token generado con estas credenciales es rechazado con un error `401 Unauthorized` por el endpoint `/banking-core`. Esto indica que la documentación es incorrecta o que la política de autorización del endpoint no está configurada para aceptar tokens de esa aplicación cliente (`appid`).
- **Impacto:** Impide que los desarrolladores legítimos o sistemas automatizados puedan consumir el endpoint `/banking-core` siguiendo la documentación oficial, causando errores de integración y pérdida de tiempo en la depuración.
- **Prueba de Concepto (PoC):**
  1. Generar un token con las credenciales de la documentación.
  2. Usar el token para realizar una petición al endpoint `/banking-core`.
  ```bash
  TOKEN="eyJ0eXAiOiJKV1Qi..." # Token generado con credenciales de la documentación
  curl -s -i -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"Mti":"0200", ...}' \
    "https://apim-transversal-dev.azure-api.net/orquestadorevertec/banking-core"
  ```
  **Respuesta del Servidor:**
  ```http
  HTTP/1.1 401 Unauthorized
  ...
  { "statusCode": 401, "message": "Unauthorized. Access token is missing or invalid." }
  ```
- **Recomendación:** Revisar y alinear la documentación con la configuración real del gateway de la API. Asegurarse de que las credenciales proporcionadas en la documentación (`client_id`) correspondan a una aplicación cliente que tenga los permisos necesarios para consumir todos los endpoints documentados.
