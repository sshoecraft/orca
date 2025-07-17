# Orca Job Orchestrator 🐋

![Orca Logo](frontend/public/orca-logo.svg)

A powerful job orchestrator designed to manage and execute commands across multiple remote systems with an intuitive web-based interface.

## 🌊 Overview

Orca is a modern job orchestration platform that enables centralized management and execution of commands across heterogeneous system environments. With support for both Windows and Linux systems, Orca provides secure, scalable, and user-friendly command execution with real-time monitoring and comprehensive audit trails.

### Key Features

- **🖥️ Multi-System Management**: Register and manage Windows and Linux systems from a single interface
- **⚡ Parallel Job Execution**: Execute commands across multiple systems simultaneously
- **📊 Real-time Monitoring**: Track job execution status with live output streaming
- **🔐 Secure Connectivity**: Support for SSH (Linux) and WinRM (Windows) with encrypted credentials
- **📝 Complete Audit Trail**: Comprehensive logging of all operations and command executions
- **🌐 Modern Web Interface**: React-based UI with the friendly Orca whale mascot
- **🔧 RESTful API**: Full-featured API with OpenAPI/Swagger documentation
- **🚀 Async Architecture**: High-performance async backend for concurrent operations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orca Web UI (React)                      │
│                   [🐋 Orca Whale Logo]                      │
├─────────────────────────────────────────────────────────────┤
│                 REST API (FastAPI/Python)                   │
├─────────────────────────────────────────────────────────────┤
│              Job Execution Engine (Python)                  │
├─────────────────────────────────────────────────────────────┤
│                PostgreSQL Database                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────┴─────────────────┐
         │                                   │
    SSH (Linux)                       WinRM (Windows)
         │                                   │
         ▼                                   ▼
   Linux Systems                      Windows Systems
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for frontend development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sshoecraft/orca.git
   cd orca
   ```

2. **Set up the environment**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your specific settings
   ```

4. **Start the backend API**
   ```bash
   python run.py
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Test the Installation

Execute the connection test to verify everything is working:

```bash
python scripts/test_connections.py
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Reference](docs/API.md)** - Complete REST API documentation
- **[User Guide](docs/USER_GUIDE.md)** - End-user instructions and tutorials
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Installation and production deployment
- **[Architecture Documentation](docs/ARCHITECTURE.md)** - System design and components
- **[Security Guide](docs/SECURITY.md)** - Security best practices and considerations
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development setup and contribution guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🎯 Success Criteria

The system meets its goals when:

1. **✅ System Registration**: Successfully register both test systems:
   - Windows system (steve-desktop): 10.16.120.5
   - Linux system (steve-tools): 10.30.167.4

2. **✅ Command Execution**: Execute `whoami` command on both systems:
   - Windows expected output: `steve-desktop\testuser`
   - Linux expected output: `testuser`

3. **✅ Web Interface**: 
   - View registered systems in the UI
   - Create and execute jobs through the web interface
   - Monitor real-time execution status
   - View captured command output

4. **✅ Reliability**: Handle connection failures gracefully with clear error messages

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Remote Access**: paramiko (SSH), pywinrm (WinRM)
- **Authentication**: JWT tokens with Fernet encryption
- **Async**: asyncio, asyncpg

### Frontend
- **Language**: TypeScript
- **Framework**: React 18 with Vite
- **UI Library**: Material-UI or Ant Design
- **State Management**: Redux Toolkit
- **HTTP Client**: Axios with interceptors

### Infrastructure
- **Database**: PostgreSQL with async support
- **Authentication**: JWT-based with role-based access control
- **Encryption**: Fernet symmetric encryption for credentials
- **Monitoring**: Structured logging with audit trails

## 🔧 Configuration

### Database Configuration
```bash
# PostgreSQL connection
DATABASE_URL=postgresql://postgres:postgres@localhost/orca
```

### Security Configuration
```bash
# JWT settings
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Encryption key for system passwords
ENCRYPTION_KEY=your-fernet-key-here
```

### Execution Engine Settings
```bash
# Job execution limits
MAX_CONCURRENT_JOBS=10
JOB_TIMEOUT_SECONDS=300
CONNECTION_TIMEOUT_SECONDS=30
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: User permissions and role management
- **Credential Encryption**: System passwords encrypted using Fernet
- **Audit Logging**: Complete trail of all user actions and system access
- **Input Validation**: Comprehensive validation to prevent injection attacks
- **Secure Communication**: HTTPS for web interface, encrypted connections to systems

## 🧪 Testing

### Unit Tests
```bash
# Run Python tests
cd backend
pytest tests/ -v --cov

# Run TypeScript tests
cd frontend
npm test
```

### Integration Tests
```bash
# Test system connections
python scripts/test_connections.py

# Test API endpoints
python -m pytest backend/tests/test_api.py
```

### Expected Test Results
- **SSH (Linux)**: `testuser` output from steve-tools (10.30.167.4)
- **WinRM (Windows)**: `steve-desktop\testuser` output from steve-desktop (10.16.120.5)

## 📊 API Examples

### Authentication
```bash
# Login to get JWT token
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### System Management
```bash
# List all systems
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/systems"

# Register a new system
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-server",
    "hostname": "192.168.1.100",
    "port": 22,
    "system_type": "linux",
    "username": "admin",
    "password": "secure-password"
  }' \
  "http://localhost:8000/api/systems"
```

### Job Execution
```bash
# Create and execute a job
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "System Check",
    "command": "whoami",
    "system_ids": ["system-uuid-1", "system-uuid-2"]
  }' \
  "http://localhost:8000/api/jobs"
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Start PostgreSQL if needed
   sudo systemctl start postgresql
   ```

2. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh scripts/*.py
   ```

3. **Python Import Errors**
   ```bash
   # Set Python path
   export PYTHONPATH="/home/steve/src/orca/backend:$PYTHONPATH"
   ```

For more detailed troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## 🤝 Contributing

We welcome contributions! Please see our [Developer Guide](docs/DEVELOPER_GUIDE.md) for:
- Development environment setup
- Code style guidelines
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: Check the `docs/` directory for comprehensive guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Community**: Join our discussions for questions and support

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Basic job orchestration
- ✅ Windows and Linux support
- ✅ Web-based interface
- ✅ Real-time monitoring

### Upcoming Features (v1.1)
- 🔄 Job scheduling and cron-like functionality
- 📈 Enhanced monitoring and metrics
- 🔧 Job templates and reusable workflows
- 🌐 Multi-tenant support

### Future Enhancements (v2.0)
- 🔐 Advanced authentication (LDAP, SSO)
- 📱 Mobile-responsive interface
- 🎨 Custom dashboard creation
- 🔄 Workflow automation with dependencies

---

🐋 **Orca Job Orchestrator** - Orchestrating your systems, one command at a time.

Made with ❤️ by the Orca team