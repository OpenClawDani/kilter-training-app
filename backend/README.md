# Kilter Backend - FastAPI Application

FastAPI backend for Kilter video analysis platform.

## Quick Start

### 1. Setup Environment
```bash
source venv/bin/activate
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Server
```bash
PYTHONPATH=$(pwd) uvicorn app.main:app --reload
```

Server will be available at: `http://localhost:8001`

## API Endpoints

### Health Check
- `GET /health` - Server status

### Authentication (Day 2)
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Videos (Day 2)
- `POST /api/videos/upload` - Upload video
- `GET /api/videos/{video_id}` - Get video status

### Circuits (Day 2)
- `GET /api/circuits/{circuit_id}` - Get circuit details

## Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI Schema**: http://localhost:8001/openapi.json

## Project Structure

```
app/
├── core/          # Core configuration (database, security, settings)
├── api/           # API routes (auth, videos, circuits)
├── services/      # Business logic services
├── tasks/         # Celery background tasks
└── main.py        # FastAPI app factory
```

## Database

### Docker Compose (PostgreSQL + Redis)
```bash
docker-compose up -d
```

### Manual Connection
Database URL: `postgresql://kilter:kilter@localhost/kilter_db`

## Testing

```bash
# Health check
curl http://localhost:8001/health

# Test endpoints
curl -X POST http://localhost:8001/api/auth/register
curl http://localhost:8001/api/videos/test-123
```

## Dependencies

See `requirements.txt` for full list. Key packages:
- fastapi
- sqlalchemy
- celery
- redis
- pydantic

## Day 2 Implementation

Ready for:
- User authentication models
- Video upload handling
- Celery task configuration
- Database migrations
