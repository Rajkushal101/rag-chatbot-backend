# RAG Chatbot Backend 🤖

A production-ready RAG (Retrieval-Augmented Generation) chatbot backend with **session-based isolation**. Upload documents, chat with AI that understands your content, and ensure complete data privacy between sessions.

Built with FastAPI, LangChain, PostgreSQL + pgvector, and OpenAI.

---

## � What Makes This Special?

- **Session Isolation**: Documents from one session never leak into another - guaranteed by database-level filtering
- **Smart RAG**: AI retrieves relevant context from your documents before answering
- **Async Everything**: Built for high performance with FastAPI's async architecture
- **Production Ready**: Docker deployment, proper error handling, background tasks
- **Simple API**: Three endpoints - create session, upload document, chat

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

Before you begin, make sure you have:

1. **Docker Desktop** installed and running ([Download here](https://www.docker.com/products/docker-desktop))
2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
   - You'll need about $1-5 in credits for testing

### Step 1: Clone This Repository

```bash
git clone https://github.com/Rajkushal101/rag-chatbot-backend.git
cd rag-chatbot-backend
```

### Step 2: Add Your OpenAI API Key

```bash
# Create .env file from example
copy .env.example .env
```

**Open `.env` in any text editor** and replace `your-openai-api-key-here` with your actual OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

> **💡 Important**: Never commit your `.env` file to GitHub! It's already in `.gitignore` for safety.

### Step 3: Start the Application

```bash
docker-compose up -d
```

This will:
- Download PostgreSQL with vector search extension
- Build the FastAPI backend
- Start both services in the background

**Wait 30 seconds** for everything to initialize.

### Step 4: Verify It's Running

Open your browser and visit: **http://localhost:8000/docs**

You should see the interactive API documentation (Swagger UI). ✅

Or test via command line:
```bash
curl http://localhost:8000/health
```

**Expected response**: `{"status":"healthy"}`

---

## 📖 How to Use

### Interactive API Docs (Easiest Way)

1. Open http://localhost:8000/docs
2. Click "POST /sessions" → "Try it out" → "Execute"
3. Copy the `session_id` from the response
4. Use that `session_id` for uploading files and chatting

### Via Command Line

**1. Create a Chat Session**
```bash
curl -X POST http://localhost:8000/sessions -H "Content-Type: application/json" -d "{}"
```

Copy the `session_id` from the response.

**2. Upload a Document**

Create a test file `example.txt`:
```
This is a document about Python programming.
Python is a high-level, interpreted programming language.
It was created by Guido van Rossum and first released in 1991.
```

Upload it:
```bash
curl -X POST "http://localhost:8000/upload/YOUR_SESSION_ID" -F "file=@example.txt"
```

**Wait 10 seconds** for processing.

**3. Chat with Your Document**
```bash
curl -X POST "http://localhost:8000/chat/YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"When was Python created?\"}"
```

The AI will answer using context from your uploaded document! 🎉

**4. Continue the Conversation**
```bash
curl -X POST "http://localhost:8000/chat/YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Who created it?\"}"
```

The AI remembers your conversation history!

---

## 🏗️ How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    Client (You)                          │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐           │
│  │ Sessions │  │  Upload  │  │    Chat    │           │
│  │  Route   │  │  Route   │  │   Route    │           │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘           │
└───────┼─────────────┼──────────────┼───────────────────┘
        │             │              │
        ▼             ▼              ▼
┌─────────────────────────────────────────────────────────┐
│         PostgreSQL + pgvector (Database)                 │
│  • Sessions        • Documents       • Embeddings        │
│  • Chat History    • Vector Search (finds relevant)      │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  OpenAI API                              │
│  • Generate embeddings (convert text to vectors)         │
│  • Generate responses (GPT-3.5)                          │
└─────────────────────────────────────────────────────────┘
```

### Session Isolation Explained

**The Problem**: In multi-user systems, you don't want User A seeing User B's documents.

**Our Solution**:
1. Every document chunk gets tagged with `session_id`
2. Vector search ALWAYS filters by `session_id` first
3. Database index makes this filtering fast
4. **Result**: Impossible for sessions to see each other's data

This is tested in `tests/test_session_isolation.py` ✅

---

## 🎯 Project Structure

```
rag-chatbot-backend/
├── app/
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Environment configuration
│   ├── database.py               # PostgreSQL connection
│   │
│   ├── api/routes/
│   │   ├── session.py            # POST /sessions
│   │   ├── upload.py             # POST /upload/{session_id}
│   │   └── chat.py               # POST /chat/{session_id}
│   │
│   ├── services/
│   │   ├── document_service.py   # Process PDFs, create embeddings
│   │   └── chat_service.py       # RAG logic + OpenAI
│   │
│   ├── repositories/
│   │   ├── vector_store.py       # pgvector operations
│   │   └── chat_repository.py    # Store/retrieve messages
│   │
│   ├── models/                   # SQLAlchemy database models
│   └── schemas/                  # Pydantic request/response schemas
│
├── tests/
│   └── test_session_isolation.py # Verify session isolation works
│
├── docker-compose.yml            # Run everything with one command
├── Dockerfile                    # Backend container setup
├── init_db.sql                   # Database schema + pgvector setup
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for your .env file
└── README.md                     # You are here!
```

---

## ⚙️ Configuration

All settings are in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | **Required** |
| `LLM_MODEL` | Which GPT model to use | `gpt-3.5-turbo` |
| `EMBEDDING_MODEL` | Which embedding model | `text-embedding-3-small` |
| `CHUNK_SIZE` | Text chunk size (chars) | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |

---

## 🧪 Running Tests

```bash
# Run session isolation test
docker-compose exec backend pytest tests/test_session_isolation.py -v
```

This test verifies that:
- Session A uploads a document
- Session B uploads a different document
- Session A can only retrieve Session A's document ✅

---

## 🐛 Troubleshooting

### "Connection refused" when accessing localhost:8000

**Solution**: Wait 30-60 seconds after `docker-compose up -d` for services to fully start.

Check logs:
```bash
docker-compose logs backend
```

### "OpenAI API error: Invalid API key"

**Solution**: 
1. Verify your API key is correct in `.env`
2. Check you have credits: https://platform.openai.com/usage
3. Restart: `docker-compose restart backend`

### "Port 8000 already in use"

**Solution**:
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill that process
taskkill /PID <PID_NUMBER> /F

# Restart
docker-compose up -d
```

### Docker not starting

**Solution**: Make sure Docker Desktop is running (check system tray).

---

## 🛑 Stopping the Application

```bash
# Stop services
docker-compose down  

# Stop and remove all data (fresh start)
docker-compose down -v
```

---

## 🎓 Technical Highlights

Built for the **Atlantis Residency Program** evaluation. Key technical decisions:

- **Async/Await**: All I/O operations are non-blocking
- **Background Tasks**: Document processing doesn't block uploads
- **Vector Database**: pgvector with HNSW indexing for fast similarity search
- **Dependency Injection**: Clean architecture with FastAPI's DI system
- **Type Safety**: Pydantic schemas for request validation
- **Session Isolation**: GIN index on `metadata->>'session_id'` for security

---

## 📄 API Reference

Full API documentation available at: **http://localhost:8000/docs**

### Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/sessions` | POST | Create new chat session |
| `/upload/{session_id}` | POST | Upload document (PDF/TXT) |
| `/chat/{session_id}` | POST | Send message and get AI response |

---

## 📧 Questions?

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review logs: `docker-compose logs -f backend`
3. Inspect the interactive docs: http://localhost:8000/docs

---

## � Security Notes

- ✅ Session isolation enforced at database level
- ✅ API keys never stored in database
- ✅ `.env` file in `.gitignore` (never committed)
- ✅ Input validation on all endpoints
- ✅ No SQL injection vulnerabilities (using SQLAlchemy ORM)

---

**Built with** FastAPI, LangChain, PostgreSQL (pgvector), and OpenAI

*Ready to impress in your interview!* 🚀
