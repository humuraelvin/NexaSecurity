# NexaSecurity API Authentication Update

This update modifies the authentication system to be fully compatible with the frontend implementation.

## Changes Made

1. **User Model Update**:

   - Renamed `name` to `full_name`
   - Renamed `company` to `company_name`
   - Renamed `plan` to `subscription_tier`
   - Added `is_active` boolean field

2. **Auth Endpoints**:

   - Updated login and signup responses to include both `access_token` and `refresh_token`
   - Modified response structure to match frontend expectations
   - Enhanced token extraction logic to handle multiple sources (cookies, Authorization header)
   - Added `/auth/profile` endpoint to retrieve the current user's profile

3. **CORS Configuration**:

   - Added explicit CORS configuration for the Authorization header
   - Enabled credentials support for cross-origin requests

4. **Database Migration**:
   - Added migration script to automatically update existing database schemas
   - Preserves existing user data by copying from old columns to new ones
   - Enhanced migration script to handle partial migrations

## How to Run the Migration Manually

If you need to run the migration manually (outside of the normal API startup):

```bash
# From the api directory
python migrate.py
```

## Authentication Flow

The authentication flow now works as follows:

1. **Login**:

   - User submits email and password to `/auth/login/json`
   - API validates credentials and returns:
     - `access_token`: Short-lived JWT token for API access
     - `refresh_token`: Long-lived token for obtaining new access tokens
     - `user`: User object with profile information

2. **Token Usage**:

   - Frontend stores tokens in localStorage with the keys `token` and `refresh_token`
   - Frontend includes access token in Authorization header with format `Bearer {token}`
   - API extracts token from header or cookies

3. **User Profile**:

   - User profile can be retrieved from `/auth/profile` with a valid token
   - Profile includes id, email, full_name, company_name, subscription_tier, and is_active

4. **Token Refresh**:

   - When access token expires, frontend sends refresh token to `/auth/refresh`
   - API issues a new access token

5. **Logout**:
   - User logs out via `/auth/logout`
   - Frontend removes tokens from localStorage
   - API clears auth cookies

## API Response Format

The login response format is now:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_name": "Example Inc",
    "subscription_tier": "basic",
    "is_active": true
  }
}
```

## Frontend Compatibility Notes

- The API now properly handles the `Authorization: Bearer {token}` header format used by the frontend
- Token storage keys in localStorage are expected to be `token` and `refresh_token`
- The user object structure matches the frontend User interface

## Testing the API

After these changes, the frontend authentication should work seamlessly with the backend API.
