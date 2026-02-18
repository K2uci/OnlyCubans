# JWT Token Not Invalidated After Logout - Persistent Session After Logout Attempt

**ID:** vuln-0004
**Severity:** HIGH
**Found:** 2026-02-17 19:13:56 UTC

## Description

## Vulnerability Summary
The MonitorPro application fails to properly invalidate JWT tokens after a user attempts to logout. The logout endpoint returns an HTTP 500 error, and the JWT tokens remain valid and functional, allowing continued access to protected API endpoints.

## Affected Application
- **Application**: MonitorPro (Fleet Tracking Platform)
- **URL**: https://almaviva.monitorpro.ai/
- **Affected Endpoint**: POST /api/users/logout
- **Vulnerable Component**: JWT Token Management / Session Invalidation

## Technical Details

### The Issue
1. The logout endpoint (`POST /api/users/logout`) returns HTTP 500 error with message: `"Argument passed in must be a single String of 12 bytes or a string of 24 hex characters"`
2. No server-side token blacklist or revocation mechanism exists
3. JWT tokens continue to function normally after logout attempt
4. All 4 token types issued remain valid until their natural expiration

### Token Lifetimes
- `token`: 4 minutes (240 seconds)
- `tokenCv`: 20 minutes (1200 seconds)
- `tokenCentralApp`: 20 minutes (1200 seconds)
- `refreshtoken`: 5 minutes (300 seconds)

## Proof of Concept

### Step 1: Login and obtain JWT token
```
POST /api/users/login HTTP/1.1
Host: almaviva.monitorpro.ai
Content-Type: application/json

{"email":"admin","password":"1futuro2@26"}
```

Response contains JWT token (HTTP 200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  ...
}
```

### Step 2: Verify token works (before logout)
```
GET /api/users/V2/maintenance/all?page=1&pageSize=10 HTTP/1.1
Host: almaviva.monitorpro.ai
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Result**: HTTP 200 - Returns 9 users successfully

### Step 3: Attempt logout
```
POST /api/users/logout HTTP/1.1
Host: almaviva.monitorpro.ai
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```
**Result**: HTTP 500 - `{"errorMsg":"Argument passed in must be a single String of 12 bytes or a string of 24 hex characters"}`

### Step 4: Verify token STILL works after logout
```
GET /api/users/V2/maintenance/all?page=1&pageSize=10 HTTP/1.1
Host: almaviva.monitorpro.ai
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Result**: HTTP 200 - Returns 9 users successfully (TOKEN STILL VALID!)

## Impact

### Security Risks
1. **Session Hijacking Persistence**: If an attacker steals a JWT token (via XSS, network sniffing, or other means), the legitimate user cannot invalidate the stolen token by logging out
2. **No Emergency Revocation**: Administrators cannot force-logout compromised accounts
3. **Shared Device Risk**: Users on shared computers cannot securely end their session
4. **Compliance Issues**: May violate security requirements for session management (OWASP, PCI-DSS)

### Attack Scenarios
- An attacker who captures a token through XSS or man-in-the-middle attack can use it for 4-20 minutes regardless of user actions
- A malicious insider with temporary access to a user's session can maintain access even after the user "logs out"
- Tokens stored in browser storage persist and remain usable even after logout

## CVSS Score Assessment
- **CVSS v3.1 Base Score**: 6.5 (Medium-High)
- **Vector**: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N

## Remediation Recommendations

### Immediate Fixes
1. **Fix the logout endpoint**: Resolve the HTTP 500 error in the logout function
2. **Implement token blacklisting**: Store invalidated tokens in a fast-access cache (Redis) until expiration
3. **Add token version/jti claim**: Include a unique identifier that can be checked against revoked tokens

### Long-term Improvements
1. **Implement token refresh rotation**: Issue new refresh tokens on each use, invalidating old ones
2. **Reduce token lifetimes**: Consider shorter expiration times for sensitive operations
3. **Add session binding**: Bind tokens to client fingerprint (IP, User-Agent) to limit replay attacks
4. **Implement forced logout**: Allow administrators to invalidate all tokens for a user

## References
- OWASP Session Management Cheat Sheet
- CWE-613: Insufficient Session Expiration
- RFC 7519: JSON Web Token (JWT)
