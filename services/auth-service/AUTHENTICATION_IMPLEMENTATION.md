# Authentication Service Implementation

## Overview

The authentication service has been fully implemented with JWT-based authentication, role-based access control (RBAC), and comprehensive user management.

## Features Implemented

### 1. Authentication Endpoints (`/api/v1/auth`)

- **POST `/api/v1/auth/register`** - Register a new user
  - Validates email, username, and password strength
  - Creates user account with hashed password
  - Returns user information

- **POST `/api/v1/auth/login`** - Login user
  - Authenticates username and password
  - Generates JWT access token and refresh token
  - Tracks failed login attempts (locks account after 5 attempts)
  - Stores refresh token in database with IP and user agent

- **POST `/api/v1/auth/refresh`** - Refresh access token
  - Uses refresh token to generate new access token
  - Validates refresh token from database

- **POST `/api/v1/auth/logout`** - Logout user
  - Revokes refresh token

- **POST `/api/v1/auth/logout-all`** - Logout from all devices
  - Revokes all refresh tokens for the user

### 2. User Management Endpoints (`/api/v1/users`)

- **GET `/api/v1/users/me`** - Get current user profile
  - Requires authentication
  - Returns user information with roles

- **PATCH `/api/v1/users/me`** - Update user profile
  - Allows updating full_name, phone, department

- **POST `/api/v1/users/me/change-password`** - Change password
  - Validates current password
  - Updates password with new hash

### 3. Security Features

- **Password Hashing**: Uses bcrypt via passlib
- **JWT Tokens**: 
  - Access tokens (30 minutes default)
  - Refresh tokens (7 days default)
  - Token validation and verification
- **Account Locking**: Locks account after 5 failed login attempts for 30 minutes
- **Failed Login Tracking**: Tracks and increments failed attempts
- **Token Revocation**: Refresh tokens stored in database and can be revoked

### 4. Authorization Dependencies

- `get_current_user` - Get authenticated user from JWT token
- `get_current_active_user` - Get active user (checks if account is active and not locked)
- `require_permission(permission_name)` - Require specific permission
- `require_role(role_name)` - Require specific role
- `require_superuser` - Require superuser privileges

### 5. Data Models

#### User Model
- Email, username (unique)
- Hashed password
- Profile fields (full_name, phone, department)
- Account status (is_active, is_verified, is_superuser)
- Security fields (failed_login_attempts, locked_until, last_login)
- Relationships to roles and refresh tokens

#### Role Model
- Name (unique)
- Description
- System flag (prevents deletion)
- Relationships to users and permissions

#### Permission Model
- Name (unique)
- Resource and action (e.g., "users:read", "anpr:write")
- Description
- Relationships to roles

#### RefreshToken Model
- Token string
- User relationship
- Expiration date
- Revocation status
- IP address and user agent tracking

## API Usage Examples

### Register User

```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User",
    "phone": "+1234567890",
    "department": "IT"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User

```bash
curl -X GET "http://localhost:8001/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token

```bash
curl -X POST "http://localhost:8001/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### Update Profile

```bash
curl -X PATCH "http://localhost:8001/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+9876543210"
  }'
```

### Change Password

```bash
curl -X POST "http://localhost:8001/api/v1/users/me/change-password" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123",
    "new_password": "NewSecurePass456"
  }'
```

## Using Authorization Dependencies

### Require Permission

```python
from app.dependencies.auth import require_permission

@app.get("/protected-endpoint", dependencies=[Depends(require_permission("users:read"))])
async def protected_endpoint():
    return {"message": "Access granted"}
```

### Require Role

```python
from app.dependencies.auth import require_role

@app.get("/admin-endpoint", dependencies=[Depends(require_role("admin"))])
async def admin_endpoint():
    return {"message": "Admin access"}
```

### Require Superuser

```python
from app.dependencies.auth import require_superuser

@app.get("/superuser-endpoint")
async def superuser_endpoint(current_user: User = Depends(require_superuser)):
    return {"message": "Superuser access"}
```

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Token Configuration

Default token expiration times for development (override via environment variables in production-sensitive deployments):
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 525,600 minutes (1 year)
- `REFRESH_TOKEN_EXPIRE_DAYS`: 365 days

## Security Features

1. **Password Strength Validation**: Enforced during registration and password change
2. **Account Locking**: Automatic locking after 5 failed login attempts
3. **Token Revocation**: Refresh tokens can be revoked individually or all at once
4. **IP and User Agent Tracking**: Stored with refresh tokens for security auditing
5. **JWT Token Validation**: All tokens are validated before use
6. **Role-Based Access Control**: Fine-grained permission system

## Next Steps

1. **Seed Initial Data**: Create initial roles and permissions
2. **Email Verification**: Add email verification flow
3. **Password Reset**: Implement password reset via email
4. **Two-Factor Authentication**: Add 2FA support
5. **Rate Limiting**: Add rate limiting for login endpoints
6. **Audit Logging**: Log all authentication events

## Testing

To test the authentication service:

1. Start the service:
   ```bash
   cd services/auth-service
   uvicorn app.main:app --reload --port 8001
   ```

2. Access Swagger UI at: `http://localhost:8001/docs`

3. Test endpoints using the interactive Swagger UI or curl commands above.

## Environment Variables

Required environment variables:
- `SECRET_KEY`: JWT secret key (change in production!)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`: Database connection
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 525600)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 365)

