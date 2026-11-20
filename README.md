# Study Buddy - AI Study Assistant

Study Buddy is an AI-powered study assistant for students, built with Flask, Tailwind CSS, and the official Google GenAI SDK (`google-genai`).

## Features
- **Interactive Web Interface**: Clean educational UI with indigo/violet styling, mobile-first responsive layout, and soft shadows.
- **5 Study Modes**:
  - 💬 **Ask Questions**: Ask any study question and get clear answers.
  - 💡 **Explain Topics (ELI5)**: Simple, intuitive explanations for complex subjects.
  - 📝 **Quiz Me**: Test your knowledge with practice questions.
  - 📄 **Summarize Notes**: Condense long notes and articles into key points.
  - 🎯 **Study Tips**: Actionable advice for exams and memorization.
- **Official Google GenAI SDK**: Powered by `google-genai` using Gemini models (default: `gemini-3.8-flash`, overridable via `GEMINI_MODEL`).
- **Resilient Fallback**: Graceful demo mode if the API key is missing or upstream service is temporarily busy.
- **Full Input Validation**: Robust handling for empty prompts and invalid modes (HTTP 400).

## Quick Start

### 1. Setup & Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Add your Gemini API key inside `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

### 3. Run the App
```powershell
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser!

## API Endpoints

- `GET /`: Renders the web interface.
- `GET /health`: JSON health check (returns app status, Gemini connectivity, and supported modes).
- `POST /api/chat`: Accepts `{ "prompt": "...", "mode": "ask" | "explain" | "quiz" | "summarize" | "tips" }` and returns `{ "response": "...", "source": "gemini" | "demo" }`.

### Testing via PowerShell
```powershell
# Health Check
Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -Method Get | ConvertTo-Json

# Chat Request with Mode
$body = @{
    prompt = "Explain photosynthesis"
    mode = "explain"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chat" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
```
