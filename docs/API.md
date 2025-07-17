# Orca Job Orchestrator - API Reference

![Orca Logo](../frontend/public/orca-logo.svg)

Comprehensive REST API documentation for the Orca Job Orchestrator.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [Systems](#systems-endpoints)
  - [Jobs](#jobs-endpoints)
  - [Dashboard](#dashboard-endpoints)
  - [Health](#health-endpoints)
- [Data Models](#data-models)
- [Examples](#examples)

## 🌐 Overview

### Base URL
```
http://localhost:8000/api
```

### API Version
```
v1.0.0
```

### Content Type
All requests and responses use JSON format:
```
Content-Type: application/json
```

### Response Format
All API responses follow a consistent structure:

```json
{
  "success": boolean,
  "data": object | array,
  "message": string,
  "timestamp": string,
  "request_id": string
}
```

## 🔐 Authentication

Orca uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

**POST** `/api/auth/token`

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## ❌ Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 422  | Validation Error |
| 500  | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Error message",
  "error_type": "ValidationError",
  "errors": [
    {
      "field": "field_name",
      "message": "Field-specific error message"
    }
  ]
}
```

## 🛡️ Rate Limiting

- **Rate Limit**: 100 requests per minute per IP
- **Headers**: Rate limit information in response headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📡 Endpoints

### Authentication Endpoints

#### Login
**POST** `/api/auth/token`

Authenticate user and receive access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
**POST** `/api/auth/refresh`

Refresh an existing token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Current User
**GET** `/api/auth/me`

Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "username": "admin",
  "roles": ["admin"],
  "permissions": ["systems:read", "systems:write", "jobs:read", "jobs:write"]
}
```

### Systems Endpoints

#### List Systems
**GET** `/api/systems`

Retrieve all registered systems.

**Query Parameters:**
- `active`: boolean - Filter by active status
- `system_type`: string - Filter by system type (linux/windows)
- `limit`: integer - Number of results (default: 50)
- `offset`: integer - Pagination offset (default: 0)

**Response:**
```json
{
  "systems": [
    {
      "id": "uuid",
      "name": "my-server",
      "hostname": "192.168.1.100",
      "port": 22,
      "system_type": "linux",
      "username": "admin",
      "is_active": true,
      "health_status": "healthy",
      "created_at": "2025-01-15T10:00:00Z",
      "last_health_check": "2025-01-15T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### Get System
**GET** `/api/systems/{system_id}`

Retrieve a specific system by ID.

**Path Parameters:**
- `system_id`: string (UUID) - System identifier

**Response:**
```json
{
  "id": "uuid",
  "name": "my-server",
  "hostname": "192.168.1.100",
  "port": 22,
  "system_type": "linux",
  "username": "admin",
  "is_active": true,
  "health_status": "healthy",
  "created_at": "2025-01-15T10:00:00Z",
  "last_health_check": "2025-01-15T12:00:00Z"
}
```

#### Create System
**POST** `/api/systems`

Register a new system.

**Request Body:**
```json
{
  "name": "my-server",
  "hostname": "192.168.1.100",
  "port": 22,
  "system_type": "linux",
  "username": "admin",
  "password": "secure-password",
  "description": "My Linux server"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "my-server",
  "hostname": "192.168.1.100",
  "port": 22,
  "system_type": "linux",
  "username": "admin",
  "is_active": true,
  "health_status": "unknown",
  "created_at": "2025-01-15T10:00:00Z"
}
```

#### Update System
**PUT** `/api/systems/{system_id}`

Update an existing system.

**Path Parameters:**
- `system_id`: string (UUID) - System identifier

**Request Body:**
```json
{
  "name": "updated-server",
  "hostname": "192.168.1.101",
  "port": 2222,
  "username": "newuser",
  "password": "new-password",
  "is_active": true
}
```

#### Delete System
**DELETE** `/api/systems/{system_id}`

Delete a system and all associated job executions.

**Path Parameters:**
- `system_id`: string (UUID) - System identifier

**Response:**
```json
{
  "message": "System deleted successfully"
}
```

#### Test System Connection
**POST** `/api/systems/{system_id}/test`

Test connectivity to a system.

**Response:**
```json
{
  "success": true,
  "response_time_ms": 145.2,
  "system_info": {
    "whoami_output": "admin",
    "hostname": "my-server",
    "os_info": "Linux my-server 5.4.0"
  }
}
```

### Jobs Endpoints

#### List Jobs
**GET** `/api/jobs`

Retrieve all jobs.

**Query Parameters:**
- `status`: string - Filter by status (pending/running/completed/failed/cancelled)
- `created_by`: string - Filter by creator
- `limit`: integer - Number of results (default: 50)
- `offset`: integer - Pagination offset (default: 0)

**Response:**
```json
{
  "jobs": [
    {
      "id": "uuid",
      "name": "System Check",
      "command": "whoami",
      "status": "completed",
      "created_by": "admin",
      "created_at": "2025-01-15T10:00:00Z",
      "executions": [
        {
          "id": "uuid",
          "system_id": "uuid",
          "system_name": "my-server",
          "status": "completed",
          "exit_code": 0,
          "stdout": "admin",
          "stderr": "",
          "duration_seconds": 1.2
        }
      ]
    }
  ],
  "total": 1
}
```

#### Create Job
**POST** `/api/jobs`

Create and execute a new job.

**Request Body:**
```json
{
  "name": "System Check",
  "command": "whoami",
  "system_ids": ["uuid1", "uuid2"],
  "schedule_at": "2025-01-15T15:00:00Z"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "System Check",
  "command": "whoami",
  "status": "pending",
  "created_by": "admin",
  "created_at": "2025-01-15T10:00:00Z",
  "executions": [
    {
      "id": "uuid",
      "system_id": "uuid1",
      "status": "pending"
    },
    {
      "id": "uuid",
      "system_id": "uuid2", 
      "status": "pending"
    }
  ]
}
```

#### Get Job
**GET** `/api/jobs/{job_id}`

Retrieve a specific job with execution details.

**Response:**
```json
{
  "id": "uuid",
  "name": "System Check",
  "command": "whoami",
  "status": "completed",
  "created_by": "admin",
  "created_at": "2025-01-15T10:00:00Z",
  "executions": [
    {
      "id": "uuid",
      "system_id": "uuid",
      "system_name": "my-server",
      "status": "completed",
      "started_at": "2025-01-15T10:01:00Z",
      "completed_at": "2025-01-15T10:01:01Z",
      "exit_code": 0,
      "stdout": "admin",
      "stderr": "",
      "duration_seconds": 1.2
    }
  ]
}
```

#### Cancel Job
**POST** `/api/jobs/{job_id}/cancel`

Cancel a running job.

**Response:**
```json
{
  "message": "Job cancelled successfully"
}
```

### Dashboard Endpoints

#### Dashboard Data
**GET** `/api/dashboard`

Retrieve dashboard statistics and metrics.

**Response:**
```json
{
  "user": {
    "authenticated": true,
    "username": "admin"
  },
  "systems": {
    "total": 5,
    "active": 4,
    "healthy": 3,
    "linux": 3,
    "windows": 2
  },
  "jobs": {
    "total": 25,
    "pending": 2,
    "running": 1,
    "completed": 20,
    "failed": 2
  },
  "executions": {
    "total": 45,
    "pending": 3,
    "running": 2,
    "completed": 35,
    "failed": 5,
    "average_duration": 2.5
  },
  "engine": {
    "status": "healthy",
    "running_jobs": 1,
    "available_slots": 9
  }
}
```

### Health Endpoints

#### Basic Health Check
**GET** `/health`

Basic service health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "orca-job-orchestrator",
  "version": "1.0.0"
}
```

#### Detailed Health Check
**GET** `/health/detailed`

Detailed health check including dependencies.

**Response:**
```json
{
  "status": "healthy",
  "service": "orca-job-orchestrator",
  "version": "1.0.0",
  "database": {
    "status": "healthy",
    "response_time_ms": 12.5,
    "active_connections": 5
  },
  "components": {
    "database": "healthy",
    "execution_engine": "healthy"
  }
}
```

## 📊 Data Models

### System Model
```json
{
  "id": "string (UUID)",
  "name": "string (unique)",
  "hostname": "string",
  "port": "integer",
  "system_type": "linux | windows",
  "username": "string",
  "is_active": "boolean",
  "health_status": "healthy | unhealthy | unknown",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "last_health_check": "string (ISO 8601)"
}
```

### Job Model
```json
{
  "id": "string (UUID)",
  "name": "string",
  "command": "string",
  "status": "pending | running | completed | failed | cancelled",
  "created_by": "string",
  "created_at": "string (ISO 8601)",
  "scheduled_at": "string (ISO 8601, optional)",
  "executions": ["JobExecution"]
}
```

### Job Execution Model
```json
{
  "id": "string (UUID)",
  "job_id": "string (UUID)",
  "system_id": "string (UUID)",
  "system_name": "string",
  "status": "pending | running | completed | failed | timeout",
  "started_at": "string (ISO 8601)",
  "completed_at": "string (ISO 8601)",
  "exit_code": "integer",
  "stdout": "string",
  "stderr": "string",
  "error_message": "string",
  "duration_seconds": "number"
}
```

## 🔧 Examples

### Complete Workflow Example

```bash
# 1. Authenticate
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Register a system
curl -X POST "http://localhost:8000/api/systems" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "hostname": "192.168.1.100",
    "port": 22,
    "system_type": "linux",
    "username": "deploy",
    "password": "secure-password"
  }'

# Response: {"id": "123e4567-e89b-12d3-a456-426614174000", ...}

# 3. Test connection
curl -X POST "http://localhost:8000/api/systems/123e4567-e89b-12d3-a456-426614174000/test" \
  -H "Authorization: Bearer eyJ..."

# Response: {"success": true, "response_time_ms": 145.2, ...}

# 4. Create and execute job
curl -X POST "http://localhost:8000/api/jobs" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "System Information",
    "command": "uname -a",
    "system_ids": ["123e4567-e89b-12d3-a456-426614174000"]
  }'

# Response: {"id": "456e7890-e89b-12d3-a456-426614174000", "status": "pending", ...}

# 5. Check job status
curl "http://localhost:8000/api/jobs/456e7890-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer eyJ..."

# Response: Job details with execution results
```

### Error Handling Example

```javascript
// JavaScript/TypeScript client example
const apiClient = {
  async request(endpoint, options = {}) {
    const response = await fetch(`http://localhost:8000/api${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`API Error: ${error.detail}`);
    }
    
    return response.json();
  },
  
  async createSystem(systemData) {
    try {
      return await this.request('/systems', {
        method: 'POST',
        body: JSON.stringify(systemData)
      });
    } catch (error) {
      console.error('Failed to create system:', error.message);
      throw error;
    }
  }
};
```

---

🐋 **Orca Job Orchestrator API** - Powerful, secure, and easy to use.