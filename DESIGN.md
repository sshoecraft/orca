# Orca Job Orchestrator - System Design

![Orca Logo](frontend/public/orca-logo.svg)

## 📋 Overview

Orca is a distributed job orchestration system designed to execute commands across heterogeneous environments (Linux and Windows) with a modern web-based interface. The system emphasizes security, scalability, and user experience.

## 🏗️ Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI["🌐 React Frontend<br/>TypeScript + Material-UI"]
        API_CLIENT["📱 API Clients<br/>REST/HTTP"]
    end
    
    subgraph "API Layer"
        GATEWAY["🚪 API Gateway<br/>FastAPI + CORS"]
        AUTH["🔐 Authentication<br/>JWT + RBAC"]
        MIDDLEWARE["⚙️ Middleware<br/>Logging + Validation"]
    end
    
    subgraph "Business Layer"
        SYSTEM_SVC["🖥️ System Service<br/>CRUD + Health Checks"]
        JOB_SVC["⚡ Job Service<br/>Creation + Management"]
        EXEC_ENGINE["🚀 Execution Engine<br/>Async Job Processing"]
    end
    
    subgraph "Data Layer"
        DB[("🗃️ PostgreSQL<br/>Systems + Jobs + Audit")]
        ENCRYPTION["🔒 Encryption<br/>Credential Storage"]
    end
    
    subgraph "Connector Layer"
        SSH_CONN["🐧 SSH Connector<br/>Linux Systems"]
        WINRM_CONN["🪟 WinRM Connector<br/>Windows Systems"]
    end
    
    subgraph "Target Systems"
        LINUX["🐧 Linux Servers<br/>SSH Port 22"]
        WINDOWS["🪟 Windows Servers<br/>WinRM Port 5985"]
    end
    
    UI --> GATEWAY
    API_CLIENT --> GATEWAY
    GATEWAY --> AUTH
    GATEWAY --> MIDDLEWARE
    AUTH --> SYSTEM_SVC
    AUTH --> JOB_SVC
    SYSTEM_SVC --> DB
    JOB_SVC --> DB
    JOB_SVC --> EXEC_ENGINE
    EXEC_ENGINE --> SSH_CONN
    EXEC_ENGINE --> WINRM_CONN
    SSH_CONN --> LINUX
    WINRM_CONN --> WINDOWS
    SYSTEM_SVC --> ENCRYPTION
    EXEC_ENGINE --> DB
```

### Component Breakdown

#### 1. Frontend Layer
- **Technology**: React 18 + TypeScript + Vite
- **UI Framework**: Material-UI (MUI) with custom theming
- **State Management**: Redux Toolkit with RTK Query
- **Routing**: React Router v6
- **Features**:
  - Responsive design for desktop and mobile
  - Real-time job monitoring with WebSocket updates
  - Dark/light theme support
  - Accessibility (WCAG 2.1 AA compliance)

#### 2. Backend API Layer
- **Framework**: FastAPI with async/await support
- **API Style**: RESTful with OpenAPI 3.0 documentation
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Features**:
  - Automatic API documentation generation
  - Request/response validation with Pydantic
  - Rate limiting and throttling
  - Comprehensive error handling

#### 3. Database Layer
- **Database**: PostgreSQL 15+ with async support
- **ORM**: SQLAlchemy 2.0 with async sessions
- **Connection Pooling**: asyncpg with connection pooling
- **Schema**: 
  - Systems table (registered systems)
  - Jobs table (job definitions)
  - Job_executions table (execution records)
  - Audit_logs table (activity tracking)

#### 4. Execution Engine
- **Architecture**: Async task queue with worker pools
- **Concurrency**: Configurable max concurrent jobs
- **Fault Tolerance**: Retry logic with exponential backoff
- **Monitoring**: Real-time status tracking and health checks

#### 5. Connector Layer
- **SSH Connector**: paramiko library for Linux systems
- **WinRM Connector**: pywinrm library for Windows systems
- **Features**:
  - Connection pooling and reuse
  - Timeout handling
  - Secure credential management
  - Command output streaming

## 🔐 Security Architecture

### Authentication & Authorization
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant DB
    
    Client->>API: Login Request
    API->>Auth: Validate Credentials
    Auth->>DB: Check User
    DB-->>Auth: User Data
    Auth-->>API: JWT Token
    API-->>Client: Access Token + Refresh Token
    
    Client->>API: API Request + Token
    API->>Auth: Validate Token
    Auth-->>API: User Context
    API-->>Client: Protected Resource
```

### Credential Security
- **Encryption**: Fernet symmetric encryption for system passwords
- **Key Management**: Environment-based encryption keys
- **Storage**: Encrypted credentials in database
- **Transmission**: HTTPS for all web traffic, encrypted connections to systems

### Access Control
- **Principle of Least Privilege**: Users only access systems they're authorized for
- **Audit Logging**: Complete trail of all user actions
- **Session Management**: Secure JWT tokens with expiration
- **Input Validation**: Comprehensive validation to prevent injection attacks

## 💾 Data Model

### Core Entities

```sql
-- Systems: Remote systems that can execute jobs
CREATE TABLE systems (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    hostname VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    system_type VARCHAR(50) CHECK (system_type IN ('linux', 'windows')),
    username VARCHAR(255) NOT NULL,
    password_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    health_status VARCHAR(50) DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs: Job definitions with commands to execute
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    command TEXT NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job Executions: Individual job runs on specific systems
CREATE TABLE job_executions (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    system_id UUID REFERENCES systems(id),
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    exit_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    error_message TEXT
);

-- Audit Logs: Activity tracking
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id UUID,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Relationship Diagram
```mermaid
erDiagram
    SYSTEMS {
        uuid id PK
        string name UK
        string hostname
        int port
        string system_type
        string username
        text password_encrypted
        boolean is_active
        string health_status
        timestamp created_at
        timestamp updated_at
    }
    
    JOBS {
        uuid id PK
        string name
        text command
        string created_by
        string status
        timestamp created_at
    }
    
    JOB_EXECUTIONS {
        uuid id PK
        uuid job_id FK
        uuid system_id FK
        string status
        timestamp started_at
        timestamp completed_at
        int exit_code
        text stdout
        text stderr
        text error_message
    }
    
    AUDIT_LOGS {
        uuid id PK
        string event_type
        string user_id
        string resource_type
        uuid resource_id
        string action
        jsonb details
        timestamp created_at
    }
    
    SYSTEMS ||--o{ JOB_EXECUTIONS : "executes on"
    JOBS ||--o{ JOB_EXECUTIONS : "creates"
```

## 🔄 Job Execution Flow

### Job Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Pending: Job Created
    Pending --> Running: Execution Started
    Running --> Completed: Success
    Running --> Failed: Error
    Running --> Timeout: Timeout Exceeded
    Failed --> [*]
    Completed --> [*]
    Timeout --> [*]
    Pending --> Cancelled: User Cancelled
    Cancelled --> [*]
```

### Execution Process
```mermaid
sequenceDiagram
    participant User
    participant API
    participant Engine
    participant Connector
    participant System
    
    User->>API: Create Job
    API->>Engine: Queue Job
    Engine->>Connector: Execute Command
    Connector->>System: SSH/WinRM Connection
    System-->>Connector: Command Output
    Connector-->>Engine: Execution Result
    Engine-->>API: Status Update
    API-->>User: Real-time Updates
```

## 🚀 Scalability Considerations

### Horizontal Scaling
- **Stateless API**: Multiple API instances behind load balancer
- **Database Scaling**: Read replicas for query performance
- **Connection Pooling**: Efficient database connection management
- **Caching**: Redis for session storage and frequent queries

### Performance Optimization
- **Async Processing**: Non-blocking I/O for all operations
- **Connection Reuse**: Persistent connections to target systems
- **Batch Operations**: Bulk operations for multiple systems
- **Resource Limits**: Configurable concurrency controls

### Monitoring & Observability
- **Health Checks**: System and component health monitoring
- **Metrics**: Performance and usage metrics collection
- **Logging**: Structured logging with correlation IDs
- **Alerting**: Automated alerts for failures and thresholds

## 🔧 Configuration Management

### Environment Configuration
```yaml
# Production Configuration Example
database:
  url: postgresql://user:pass@db-cluster/orca
  pool_size: 20
  echo: false

security:
  secret_key: ${SECRET_KEY}
  encryption_key: ${ENCRYPTION_KEY}
  token_expire_minutes: 30

execution:
  max_concurrent_jobs: 50
  job_timeout_seconds: 600
  connection_timeout_seconds: 30

logging:
  level: INFO
  format: json
  output: stdout
```

### Feature Flags
- **Real-time Updates**: Enable/disable WebSocket updates
- **Health Checks**: Automatic system health monitoring
- **Audit Logging**: Detailed activity tracking
- **Rate Limiting**: API request throttling

## 🛡️ Disaster Recovery

### Backup Strategy
- **Database Backups**: Daily automated backups with point-in-time recovery
- **Configuration Backups**: Version-controlled configuration files
- **Credential Recovery**: Secure key escrow for encryption keys

### High Availability
- **Multi-AZ Deployment**: Geographic distribution
- **Load Balancing**: Multiple API instances
- **Database Clustering**: PostgreSQL clustering with failover
- **Health Monitoring**: Automated failover triggers

## 📈 Future Enhancements

### Phase 2 Features
- **Job Scheduling**: Cron-like job scheduling
- **Workflow Engine**: Multi-step job dependencies
- **Plugin System**: Custom connectors and processors
- **Advanced Monitoring**: Metrics dashboard and alerting

### Phase 3 Features
- **Multi-tenancy**: Organization and team isolation
- **Advanced RBAC**: Fine-grained permissions
- **Integration APIs**: Third-party tool integrations
- **Mobile App**: Native mobile application

---

🐋 **Orca Job Orchestrator** - Designed for scale, built for reliability.