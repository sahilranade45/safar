# Safar — Developer & Operations Guide 🛠️

## 1. Local Environment Setup

### Environment Variables
Ensure `.env` exists in root:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=8000
VITE_API_BASE_URL=http://localhost:8000
```

---

## 2. Backend Commands

```bash
cd backend

# Create virtual environment
python -m venv ..\.venv

# Activate (Windows)
..\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start dev server with auto-reload
uvicorn app.main:app --reload --port 8000

# Run Pytest suite
python -m pytest
```

---

## 3. Frontend Commands

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Production Build
npm run build
```

---

## 4. API Endpoints Reference

- **`GET /health`**: Health check & system status.
- **`GET /api/config/status`**: Verify Google Gemini API key configuration.
- **`POST /api/plan/generate`**: Primary endpoint to initiate multi-agent travel plan generation.
- **`POST /api/plan/replan`**: Endpoint to request feedback-based replanning.
