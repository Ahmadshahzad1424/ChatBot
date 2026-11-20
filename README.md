# 🎓 Study Buddy - AI Study Assistant

> **"Your AI-Powered Learning Companion"**

Study Buddy is a modern, student-centric web app built with Python (Flask), Tailwind CSS, and Google's official `google-genai` SDK using `gemini-3.8-flash`. It transforms complex study materials into clear explanations, interactive quizzes, note summaries, and actionable study tips.

---

## 🌟 Key Features

1. **5 AI Personas via Prompt Engineering**:
   - 💬 **Ask Questions**: A friendly peer tutor that explains concepts concisely, defines new terms, and ends with a follow-up comprehension question.
   - 💡 **Explain Topics (ELI5)**: Uses the Feynman technique with vivid real-world analogies, no confusing jargon, and concludes with an *"In short: ..."* summary.
   - 📝 **Quiz Me**: Generates 3 multiple-choice questions of increasing difficulty with an interactive `<details>` spoiler answer key so students can test themselves first.
   - 📄 **Summarize Notes**: Synthesizes notes into three structured sections: **💡 Core Concept**, **📌 Key Takeaways**, and **⚠️ Common Pitfalls**.
   - 🎯 **Study Tips**: Evidence-based study strategies including active recall prompts, a 14-day spaced repetition schedule, a practical exercise, and exam-day tips.

2. **Polished Interactive Frontend**:
   - Clean, educational aesthetic with an indigo/violet palette and soft shadows.
   - **Rendered Markdown**: Powered by `marked.js` and securely sanitized against XSS using `DOMPurify`.
   - **Clickable Sample Chips**: Instant one-click sample topics (*Quantum Computing, Photosynthesis, Newton's Laws, DNA Replication*).
   - **1-Click Copy**: Copies raw Markdown to clipboard with a 2-second floating toast.
   - **Keyboard Shortcut**: Press <kbd>Ctrl + Enter</kbd> (or <kbd>Cmd + Enter</kbd> on macOS) to submit.

3. **🔊 Audio Readout (Text-to-Speech)**:
   - Built with the browser's native Web Speech API (`window.speechSynthesis`) — zero extra dependencies.
   - Intelligent text cleaner strips markdown syntax and prevents quiz answers from being spoiled out loud.
   - Includes Listen, Pause/Resume, and Stop controls.

4. **Resilient Architecture**:
   - If no API key is provided or the upstream model is busy, Study Buddy gracefully falls back to interactive demo responses without crashing.
   - Comprehensive error logging using Python's standard `logging` module.

---

## 📸 Screenshots

### 1. Main Dashboard & Mode Selector
```
+-------------------------------------------------------------------------+
|                                🎓 Study Buddy                           |
|                    Your AI-Powered Learning Companion                   |
|                                                                         |
|  [ 💬 Ask Questions ] [ 💡 Explain (ELI5) ] [ 📝 Quiz Me ] ...          |
|  +-------------------------------------------------------------------+  |
|  | Type your question or paste your study material...                |  |
|  +-------------------------------------------------------------------+  |
|  Try an example: [ ⚛️ Quantum Computing ] [ 🌿 Photosynthesis ] ...      |
|                                            [ Clear ] [ Ask Study Buddy ✨] |
+-------------------------------------------------------------------------+
```
*(Screenshot 1: Clean indigo-violet interface with 5 mode tabs, dynamic placeholders, and clickable example chips.)*

### 2. Interactive Quiz Mode with Answer Spoilers
```
+-------------------------------------------------------------------------+
| 🤖 Quiz Me                                             [✨ Gemini AI] [📋]|
| ----------------------------------------------------------------------- |
| 1. (Easy) What is the main pigment involved in photosynthesis?          |
|    - A) Hemoglobin    - B) Chlorophyll   - C) Melanin   - D) Keratin    |
|                                                                         |
| ▶ <Click to reveal answers>                                             |
|   - Q1: B - Chlorophyll absorbs light energy primarily in blue/red.     |
+-------------------------------------------------------------------------+
```
*(Screenshot 2: Generated multi-choice quiz with clickable answer spoiler tag rendered using marked.js & DOMPurify.)*

### 3. Audio Readout Controls & Spaced Repetition Schedule
```
+-------------------------------------------------------------------------+
| 🤖 Study Tips                               [🔊 Listen] [⏸️ Pause] [⏹️ Stop] |
| ----------------------------------------------------------------------- |
| ### 🧠 Active Recall Prompts                                            |
| ### 📅 Spaced Repetition Schedule (Day 1, 3, 7, 14)                     |
| ### 🎯 Exam-Day Advice                                                  |
+-------------------------------------------------------------------------+
```
*(Screenshot 3: Structured study strategies with live Web Speech API audio playback controls.)*

---

## 🚀 Setup Instructions

### 1. Get a Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account and click **Get API key**.
3. Create a free API key and copy it.

---

### 2. Installation & Running

#### 💻 On Windows (PowerShell)
```powershell
# 1. Clone the repository
git clone https://github.com/Ahmadshahzad1424/ChatBot.git
cd ChatBot

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
Copy-Item .env.example .env

# Edit .env and paste your GEMINI_API_KEY
# GEMINI_API_KEY=your_actual_key_here

# 5. Run the application
python app.py
```

#### 🍎 On macOS / Linux (Terminal)
```bash
# 1. Clone the repository
git clone https://github.com/Ahmadshahzad1424/ChatBot.git
cd ChatBot

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env

# Edit .env and paste your GEMINI_API_KEY
# GEMINI_API_KEY=your_actual_key_here

# 5. Run the application
python3 app.py
```

---

## 🌐 Opening the App
Once started, open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🛠️ API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the interactive Tailwind web interface |
| `/health` | `GET` | Health check (`status`, `gemini_connected`, `model`, `supported_modes`) |
| `/api/chat` | `POST` | Processes study prompts with persona instructions |

### Test with PowerShell:
```powershell
# Test Quiz Me mode
$body = @{
    prompt = "Newton's laws of motion"
    mode = "quiz"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chat" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
```

---

## 💡 Challenge Ideas (Take It Further!)
Want to extend Study Buddy? Here are great features to build next:
- 🌙 **Dark Mode**: Add a theme switcher using Tailwind's `dark:` classes.
- 🗂️ **Interactive Flashcards**: Flip cards using CSS 3D transforms for quick memorization.
- 💬 **Conversation History**: Store chat turns in local storage or session state for multi-turn tutoring.
- 📄 **PDF / Notes Upload**: Add `pdfminer.six` or `PyPDF2` to upload lecture slide PDFs and summarize them directly.
- ☁️ **Deploy Online**: Deploy to Google Cloud Run, Render, or Railway with a single Dockerfile.
