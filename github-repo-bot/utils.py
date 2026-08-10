#!/usr/bin/env python3
"""
Utility functions for GitHub Repository Enhancement Bot
"""

import os
import re
import json
import random
import string
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class CommitMessageGenerator:
    """Generate professional, realistic commit messages"""
    
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def generate_message(self, commit_type: str, developer: Dict[str, str]) -> str:
        """Generate a commit message based on type and developer profile"""
        templates = self.config["commit_templates"][commit_type]
        template = random.choice(templates)
        
        # Replace placeholders with realistic values
        replacements = {
            "feature": random.choice(self.config["features"]),
            "component": random.choice(self.config["components"]),
            "tech": random.choice(self.config["technologies"]),
            "issue": "authentication flow vulnerability",
            "scenario": "high-load production environment",
            "tool": random.choice(["ESLint", "Prettier", "Black", "Flake8"]),
            "section": random.choice(["API", "Authentication", "Database", "Frontend"])
        }
        
        for placeholder, value in replacements.items():
            template = template.replace(f"{{{placeholder}}}", value)
        
        return template

class FileContentGenerator:
    """Generate realistic file content for different programming languages"""
    
    @staticmethod
    def generate_python_file(filename: str, purpose: str = "module") -> str:
        """Generate Python file content"""
        if filename == "main.py":
            return '''#!/usr/bin/env python3
"""
Main application entry point
Professional-grade application server
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Application:
    """Main application class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.start_time = datetime.now()
        logger.info("Application initialized successfully")
    
    def run(self) -> None:
        """Start the application"""
        try:
            logger.info("Starting application server...")
            self._setup_environment()
            self._start_services()
            logger.info("Application running successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            sys.exit(1)
    
    def _setup_environment(self) -> None:
        """Setup application environment"""
        required_vars = ["DATABASE_URL", "SECRET_KEY", "API_HOST"]
        for var in required_vars:
            if not os.getenv(var):
                logger.warning(f"Environment variable {var} not set")
    
    def _start_services(self) -> None:
        """Initialize and start application services"""
        logger.info("Services started successfully")

if __name__ == "__main__":
    app = Application()
    app.run()
'''
        elif filename == "utils.py":
            return '''"""
Utility functions for application
Professional helper functions and common operations
"""

import os
import json
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt using secure algorithm"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    return password_hash.hex(), salt

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_timestamp(dt: datetime) -> str:
    """Format datetime for API responses"""
    return dt.replace(tzinfo=timezone.utc).isoformat()

class ConfigManager:
    """Configuration management utility"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
'''
        elif filename == "config.py":
            return '''"""
Application configuration management
Environment-based configuration system
"""

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    secret_key: str
    jwt_expiry_hours: int = 24
    password_min_length: int = 8
    max_login_attempts: int = 5

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool
    host: str
    port: int
    database: DatabaseConfig
    security: SecurityConfig
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            host=os.getenv('HOST', 'localhost'),
            port=int(os.getenv('PORT', '8000')),
            database=DatabaseConfig(
                url=os.getenv('DATABASE_URL', 'sqlite:///app.db'),
                pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
                echo=os.getenv('DB_ECHO', 'False').lower() == 'true'
            ),
            security=SecurityConfig(
                secret_key=os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
                jwt_expiry_hours=int(os.getenv('JWT_EXPIRY_HOURS', '24')),
                password_min_length=int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
            )
        )

# Global configuration instance
config = AppConfig.from_environment()
'''
        else:
            return f'"""\n{filename} - Professional module\nImplementation for enterprise application\n"""\n\n# Module implementation\npass\n'

    @staticmethod
    def generate_javascript_file(filename: str) -> str:
        """Generate JavaScript file content"""
        if filename == "index.js":
            return '''/**
 * Main application entry point
 * Professional Node.js server implementation
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { createLogger, format, transports } = require('winston');

// Configure logger
const logger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  transports: [
    new transports.File({ filename: 'error.log', level: 'error' }),
    new transports.File({ filename: 'combined.log' }),
    new transports.Console({
      format: format.simple()
    })
  ]
});

class Application {
  constructor() {
    this.app = express();
    this.port = process.env.PORT || 3000;
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    // Security middleware
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
      credentials: true
    }));

    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP'
    });
    this.app.use(limiter);

    // Request parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
  }

  setupRoutes() {
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    });

    // API routes
    this.app.use('/api', require('./routes'));

    // Error handling
    this.app.use((err, req, res, next) => {
      logger.error(err.stack);
      res.status(500).json({
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
      });
    });
  }

  start() {
    this.app.listen(this.port, () => {
      logger.info(`Server running on port ${this.port}`);
    });
  }
}

// Start application
if (require.main === module) {
  const app = new Application();
  app.start();
}

module.exports = Application;
'''
        else:
            return f'/**\n * {filename}\n * Professional module implementation\n */\n\nmodule.exports = {{\n  // Implementation here\n}};\n'

def generate_readme_content(project_name: str, language: str) -> str:
    """Generate professional README content"""
    return f'''# {project_name.title()} 🚀

A professional, scalable {language} application built with modern development practices and enterprise-grade architecture.

## Features

✨ **Core Functionality**
- High-performance API with comprehensive error handling
- Secure authentication and authorization system
- Real-time data processing and analytics
- Scalable microservices architecture
- Comprehensive logging and monitoring

🛡️ **Security**
- JWT-based authentication
- Rate limiting and DDoS protection
- Input validation and sanitization
- Security headers and CORS configuration
- Encrypted data storage

📊 **Performance**
- Optimized database queries
- Caching layer implementation
- Asynchronous processing
- Load balancing ready
- Performance monitoring

## Quick Start

### Prerequisites

- {language.title()} {'3.8+' if language == 'python' else '14+' if language == 'javascript' else '4.0+'}
- Database (PostgreSQL recommended)
- Redis (for caching)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/{project_name}.git
cd {project_name}

# Install dependencies
{'pip install -r requirements.txt' if language == 'python' else 'npm install'}

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
{'python manage.py migrate' if language == 'python' else 'npm run db:migrate'}

# Start the application
{'python main.py' if language == 'python' else 'npm start'}
```

## API Documentation

The API follows RESTful conventions and includes comprehensive documentation.

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "user@example.com", "password": "secure_password"}}'
```

### Core Endpoints

- `GET /api/health` - Health check
- `POST /api/auth/login` - User authentication
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Application   │    │    Database     │
│    (Nginx)      │───▶│     Server      │───▶│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │      Cache      │
                       │     (Redis)     │
                       └─────────────────┘
```

## Development

### Code Quality

This project maintains high code quality standards:

- **Linting**: {'Flake8, Black' if language == 'python' else 'ESLint, Prettier'}
- **Testing**: {'pytest' if language == 'python' else 'Jest'} with {'90%+' if language == 'python' else '85%+'} coverage
- **Type Safety**: {'mypy' if language == 'python' else 'TypeScript'} for type checking
- **Security**: Regular dependency audits and security scanning

### Running Tests

```bash
# Run all tests
{'pytest' if language == 'python' else 'npm test'}

# Run with coverage
{'pytest --cov=src' if language == 'python' else 'npm run test:coverage'}

# Run linting
{'flake8 src/' if language == 'python' else 'npm run lint'}
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Deployment

### Docker

```bash
# Build image
docker build -t {project_name} .

# Run container
docker run -p 8000:8000 {project_name}
```

### Production

The application is production-ready with:

- Environment-based configuration
- Health check endpoints
- Graceful shutdown handling
- Comprehensive logging
- Performance monitoring
- Security hardening

## Monitoring

Monitor application health and performance:

- **Health**: `/api/health` endpoint
- **Metrics**: Prometheus metrics at `/metrics`
- **Logs**: Structured JSON logging
- **Alerts**: Configurable alerting rules

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- 📧 Email: support@{project_name}.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/{project_name}/issues)
- 📖 Docs: [Documentation](https://docs.{project_name}.com)

## Acknowledgments

- Built with modern {language.title()} best practices
- Inspired by enterprise-grade application architecture
- Community-driven development approach
'''