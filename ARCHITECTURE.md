# MindGuardian AI - Complete Architecture

## Project Structure

```
Mindguardian-AI/
├── frontend/                    # Frontend (existing)
│   ├── index.html
│   ├── session.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── backend/                     # FastAPI Backend (NEW)
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration management
│   ├── models.py                # SQLAlchemy models
│   ├── database.py              # Database connection
│   ├── schemas.py               # Pydantic schemas
│   ├── auth.py                  # Authentication & JWT
│   ├── cache.py                 # Redis caching
│   ├── migrations.py            # Database migrations
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment template
│   ├── routes/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── users.py             # User auth & profile
│   │   ├── sessions.py          # Session management
│   │   ├── decisions.py         # Decisions & interventions
│   │   ├── analytics.py         # Analytics & reporting
│   │   └── health.py            # Health checks
│   └── tests/                   # Backend tests
│
├── docker-compose.yml           # Multi-container setup
├── Dockerfile.backend           # Backend container
├── BACKEND_SETUP.md            # Setup instructions
└── README.md                    # Project documentation
```

## Architecture Overview

### Frontend → Backend Flow

```
┌─────────────────────────────────────┐
│  Frontend (Vanilla JS)              │
│  - Vision Engine (MediaPipe)        │
│  - Audio Engine (Web Audio API)     │
│  - Feature Fusion (Local)           │
│  - Decision Engine (Local)          │
└──────────────┬──────────────────────┘
               │ HTTPS/WSS
               ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (Python)           │
│  - Authentication & JWT             │
│  - Session Management               │
│  - Metrics Persistence              │
│  - Decision Logging                 │
│  - Analytics & Reports              │
│  - Real-time Updates (WebSocket)    │
└──────────────┬──────────────────────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
   PostgreSQL Redis  Ollama
   (Database) (Cache) (LLM)
```

## Key Features

### 1. Privacy-First Architecture

- ✅ **Local Processing**: Vision/audio processing happens in browser
- ✅ **Optional Backend**: Backend is optional, backend functions are optional
- ✅ **Encrypted Storage**: Sensitive data encrypted at rest
- ✅ **User Control**: Users decide what data is stored/deleted
- ✅ **No Cloud Dependencies**: Works offline-first

### 2. Multimodal AI Pipeline

- **Vision Engine**: Face detection, expressions, head pose, eye tracking
- **Audio Engine**: Voice activity, pitch, speech rate, noise analysis
- **Feature Fusion**: Combines multimodal signals into cognitive indicators
- **Local LLM**: Generates decisions using local models (Ollama)
- **Decision Engine**: Rule-based + LLM hybrid decision making

### 3. Real-time Monitoring

- **Metric Ingestion**: Frontend streams metrics continuously
- **Real-time Analysis**: Backend processes streams and generates decisions
- **WebSocket Updates**: Push notifications for interventions
- **Dashboard**: Live wellness indicators and recommendations

### 4. Session Management

- **Session Lifecycle**: Start → Run → End with aggregation
- **Metric Storage**: High-resolution frame-level metrics
- **Decision Tracking**: All AI decisions logged for audit trail
- **Intervention History**: Track user response to recommendations

### 5. Analytics & Reporting

- **Dashboard Stats**: Overview of wellness trends
- **Wellness Trends**: Historical analysis over days/weeks/months
- **Report Generation**: PDF/JSON/CSV reports
- **Data Export**: User can download personal data (GDPR compliance)

## Technology Stack

### Frontend
- **HTML5, CSS3, Vanilla JavaScript (ES6)**
- **MediaPipe** - Face mesh detection
- **Web Audio API** - Audio processing
- **Canvas API** - Real-time visualization

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for database
- **PostgreSQL** - Primary database
- **Redis** - Caching & session store
- **Pydantic** - Data validation
- **Python-Jose** - JWT authentication
- **Passlib** - Password hashing

### Deployment
- **Docker** - Container orchestration
- **Docker Compose** - Multi-service setup
- **Render/Railway** - Cloud hosting options
- **Ollama** - Local LLM serving

## Data Models

### Core Entities

1. **User**: Authentication, profile, privacy settings
2. **Session**: Monitoring period with aggregated metrics
3. **SessionMetric**: Frame-level data (vision + audio)
4. **Decision**: AI recommendations and assessments
5. **Intervention**: Actions taken and user feedback
6. **Report**: Generated analytics reports

### Relationships

```
User (1) ──┬─→ (Many) Session
           └─→ (1) UserPreferences

Session (1) ──┬─→ (Many) SessionMetric
              ├─→ (Many) Decision
              └─→ (Many) Intervention

Decision (1) ──→ (0..1) Intervention
```

## API Conventions

### Authentication

All protected endpoints require JWT token:

```
Authorization: Bearer <token>
```

### Response Format

```json
{
  "status": "success",
  "data": { /* response data */ },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Handling

```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Deployment Options

### Development

```bash
docker-compose up -d
```

### Production

1. **Railway**: Connect GitHub repo, auto-deploy
2. **Render**: Deploy from git with environment variables
3. **Self-hosted**: Docker on VPS with nginx reverse proxy

## Security Considerations

- ✅ JWT for stateless authentication
- ✅ Password hashing with bcrypt
- ✅ CORS configuration for frontend
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Rate limiting (future)
- ✅ HTTPS/TLS in production

## Performance Optimization

- ✅ Redis caching for frequently accessed data
- ✅ Database indexing on important fields
- ✅ Async/await for non-blocking operations
- ✅ Connection pooling for database
- ✅ Pagination for large result sets
- ✅ Batch processing for metrics ingestion

## Next Steps

1. **Setup Development Environment**
   ```bash
   docker-compose up -d
   cd backend && python migrations.py
   ```

2. **Test Backend API**
   - Visit http://localhost:8000/docs
   - Test endpoints with Swagger UI

3. **Connect Frontend to Backend**
   - Update frontend fetch URLs
   - Add authentication token handling
   - Implement metric ingestion endpoint

4. **Deploy to Production**
   - Configure environment variables
   - Set up database backups
   - Enable monitoring & logging

## Documentation

- **API Docs**: http://localhost:8000/docs
- **Setup Guide**: See `BACKEND_SETUP.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Contributing**: See `CONTRIBUTING.md`

## Support

For questions or issues:
1. Check GitHub Issues
2. Review documentation
3. Open new issue with details
