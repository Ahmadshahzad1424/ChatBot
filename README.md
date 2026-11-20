# Study Buddy - AI Study Assistant Backend MVP

Study Buddy is a lightweight Flask backend designed to assist students with AI-powered study help, built with Python and the official Google GenAI SDK (`google-genai`).

## Features
- **Official Google GenAI SDK**: Powered by `google-genai` using Gemini models (defaulting to `gemini-3.8-flash`).
- **Flexible Configuration**: Model name, port, and API credentials can be easily configured via `.env`.
- **Health Check (`GET /`)**: Quick endpoint to verify app status and Gemini API key connectivity.
- **Study Chat Endpoint (`POST /api/chat`)**: Accepts student questions and returns AI-generated explanations and study advice.
- **Robust Fallback & Validation**:
  - Missing/empty prompts return clear `400 Bad Request` responses.
  - Missing API key or API call failures gracefully fallback to friendly demo responses without crashing.
  - All errors and operational events are logged using Python's standard `logging` module.

## Setup Instructions

### 1. Clone & Navigate
```powershell
git clone https://github.com/Ahmadshahzad1424/ChatBot.git
cd ChatBot
```

### 2. Create Virtual Environment & Install Dependencies
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and add your Gemini API key from [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=5000
```

### 4. Run the Server
```powershell
python app.py
```

## API Reference

### `GET /`
Returns backend health status and connection state.

**Example Response:**
```json
{
  "app": "Study Buddy",
  "status": "healthy",
  "gemini_connected": true,
  "model": "gemini-3.8-flash"
}
```

### `POST /api/chat`
Ask study questions.

**Request:**
```json
{
  "prompt": "Explain the difference between mitosis and meiosis simply."
}
```

**Response (Gemini):**
```json
{
  "response": "Mitosis produces two identical cells for growth and repair, while meiosis produces four genetically unique cells for reproduction.",
  "source": "gemini"
}
```

**Response (Demo Fallback):**
```json
{
  "response": "Hello! I am Study Buddy, your AI study assistant (Demo Mode)...",
  "source": "demo",
  "note": "GEMINI_API_KEY is missing or not configured in .env. Returning demo response."
}
```

## Testing with PowerShell

```powershell
# Health Check
Invoke-RestMethod -Uri "http://127.0.0.1:5000/" -Method Get | ConvertTo-Json

# Chat Request
$body = @{ prompt = "Explain Newton's third law of motion." } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chat" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
```
