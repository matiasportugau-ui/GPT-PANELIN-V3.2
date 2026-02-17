# Panelin Chat Feature

## Overview

The Panelin Chat Feature provides an interactive web interface for customers to communicate with the Panelin BMC Uruguay assistant. This feature integrates the frontend chat UI with backend AI processing and conversation persistence.

## Architecture

### Components

1. **Frontend (`frontend/`):**
   - Modern HTML/CSS/JS chat interface
   - Responsive design with gradient styling
   - Real-time message handling
   - Typing indicators and error handling
   - Spanish language interface

2. **Backend (`backend/`):**
   - Flask REST API for chat processing
   - PostgreSQL conversation storage (optional)
   - Keyword-based response generation
   - Integration point for Wolf API KB Write

### Communication Flow

```
User → Frontend (port 8080) → Backend API (port 8081) → Database (optional)
                                     ↓
                               Wolf API (future)
```

## Features

### Current Functionality

- ✅ Chat interface with modern UI
- ✅ Real-time message exchange
- ✅ Keyword-based responses (cotización, precio, ayuda)
- ✅ Error handling and fallback responses
- ✅ Conversation storage (when database available)
- ✅ Health check endpoints

### Upcoming Features

- ⏳ Integration with Wolf API KB Write endpoints
- ⏳ AI-powered responses using GPT
- ⏳ Conversation history retrieval
- ⏳ Customer data persistence
- ⏳ Real-time product quotations

## API Endpoints

### Frontend Endpoints

- `GET /` - Serves the chat interface
- `POST /api/chat` - Processes chat messages (proxies to backend)
- `GET /api/status` - Service status and backend connectivity
- `GET /health` - Health check

### Backend Endpoints

- `POST /api/chat` - Main chat processing endpoint
- `GET /api/conversations?user_id={id}` - Get conversation history
- `GET /api/data` - Database connectivity test
- `GET /health` - Health check

## Installation & Running

### Prerequisites

```bash
pip install flask requests
```

### Local Development

1. **Start Backend:**
```bash
cd backend
PORT=8081 python3 main.py
```

2. **Start Frontend:**
```bash
cd frontend
BACKEND_SERVICE_URL=http://localhost:8081 PORT=8080 python3 main.py
```

3. **Access Chat:**
Open browser to `http://localhost:8080`

### Docker Deployment

Frontend and backend each have their own Dockerfile for containerized deployment to GCP Cloud Run.

## Environment Variables

### Frontend
- `PORT` - Server port (default: 8080)
- `BACKEND_SERVICE_URL` - Backend API URL

### Backend
- `PORT` - Server port (default: 8080)
- `PROJECT_ID` - GCP project ID (for Cloud SQL)
- `DB_CONNECTION_NAME` - Cloud SQL connection name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name

## Database Schema

### conversations Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Necesito una cotización"}'
```

### Expected Response

```json
{
  "status": "success",
  "response": "¡Claro! Puedo ayudarte con una cotización...",
  "db_stored": false
}
```

## Future Integration

### Wolf API KB Write

The backend is designed to integrate with Wolf API v3.4 endpoints:

- `persist_conversation` - Save conversation summaries
- `register_correction` - Log KB corrections
- `save_customer` - Store customer data
- `lookup_customer` - Retrieve customer info

Integration points marked with `TODO` comments in the code.

## Security Considerations

- All write operations to Wolf API require password authentication
- User input is sanitized before processing
- CORS should be configured for production
- HTTPS required for production deployment
- Environment variables for sensitive configuration

## Development Notes

- Database is optional for local development
- Keyword-based responses are temporary placeholders
- Frontend uses vanilla JavaScript (no frameworks)
- Backend gracefully handles missing database
- All responses in Spanish

## Version History

- **v1.0** - Initial chat interface implementation
  - HTML/CSS/JS frontend
  - Flask backend with keyword responses
  - Conversation persistence to PostgreSQL
  - Basic error handling

---

**Last Updated:** 2026-02-17  
**Status:** In Development  
**Next Milestone:** Wolf API Integration
