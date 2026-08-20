# MindGuardian AI Backend Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional but recommended)

## Installation

### 1. Create Python Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=postgresql://mindguardian:password@localhost:5432/mindguardian_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret
LLM_ENDPOINT=http://localhost:11434
```

### 4. Initialize Database

```bash
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

## Running Locally

### Option A: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

The backend will be available at `http://localhost:8000`

### Option B: Local Development

#### Start PostgreSQL

```bash
# On macOS with Homebrew
brew services start postgresql

# On Linux
sudo systemctl start postgresql

# Or use Docker
docker run -d --name mindguardian-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=mindguardian_db \
  -p 5432:5432 \
  postgres:16-alpine
```

#### Start Redis

```bash
# On macOS with Homebrew
brew services start redis

# On Linux
sudo systemctl start redis

# Or use Docker
docker run -d --name mindguardian-redis \
  -p 6379:6379 \
  redis:7-alpine
```

#### Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - Login and get token
- `GET /api/v1/users/me` - Get current user profile
- `DELETE /api/v1/users/me` - Delete account

### Sessions

- `POST /api/v1/sessions/start` - Start monitoring session
- `GET /api/v1/sessions` - List user sessions
- `GET /api/v1/sessions/{id}` - Get session details
- `POST /api/v1/sessions/{id}/metrics` - Ingest real-time metrics
- `POST /api/v1/sessions/{id}/end` - End session
- `GET /api/v1/sessions/{id}/metrics` - Get session metrics

### Decisions

- `GET /api/v1/decisions` - List decisions
- `GET /api/v1/decisions/{id}` - Get decision details
- `POST /api/v1/decisions/{id}/acknowledge` - Acknowledge decision
- `POST /api/v1/decisions/{id}/feedback` - Provide feedback
- `GET /api/v1/decisions/interventions` - List interventions
- `POST /api/v1/decisions/{id}/interventions/execute` - Execute intervention
- `POST /api/v1/decisions/{id}/interventions/feedback` - Rate intervention

### Analytics

- `GET /api/v1/analytics/dashboard` - Dashboard statistics
- `GET /api/v1/analytics/wellness-trends` - Wellness trends
- `POST /api/v1/analytics/reports` - Generate report
- `GET /api/v1/analytics/reports` - List reports

### Health

- `GET /api/v1/health/status` - System health check
- `GET /api/v1/health/` - API information

## Interactive API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test with curl

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Start session (replace TOKEN)
TOKEN="your-token-here"
curl -X POST http://localhost:8000/api/v1/sessions/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Session",
    "activity_type": "coding"
  }'
```

## Database Management

### Connect to PostgreSQL

```bash
psql -U mindguardian -d mindguardian_db
```

### View Tables

```sql
\dt
```

### Clear All Data (Development Only)

```bash
# Using psql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## Deployment

### Deploy to Render

```bash
# Create render.yaml
services:
  - type: web
    name: mindguardian-backend
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "uvicorn backend.main:app --host 0.0.0.0"
```

### Deploy to Railway

```bash
# Link repository and deploy
railway up
```

### Deploy to DigitalOcean App Platform

See `do-app.yaml` for configuration.

## Monitoring

### View Logs

```bash
# Docker
docker-compose logs -f backend

# Local
grep -r "ERROR\|WARNING" logs/
```

### Performance Monitoring

- Check database query performance with PostgreSQL explain plans
- Monitor Redis cache hit rates
- Use FastAPI middleware for request timing

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -U mindguardian -d mindguardian_db -c "SELECT 1"

# Check connection string
echo $DATABASE_URL
```

### Redis Connection Issues

```bash
# Test connection
redis-cli ping

# Check configuration
redis-cli CONFIG GET maxmemory
```

### Clear Cache

```bash
redis-cli FLUSHALL
```

## Development

### Code Style

```bash
# Format code
black backend/

# Check style
flake8 backend/

# Type checking
mypy backend/
```

### Add Dependencies

```bash
pip install new-package
pip freeze > requirements.txt
```

## Support

For issues, check the logs or open a GitHub issue with:
- Error message
- Steps to reproduce
- Environment details (OS, Python version, etc.)
