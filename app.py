import logging
import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Gemini model constant at top of file, overridable with GEMINI_MODEL env var
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODEL = "gemini-2.5-flash"

# Valid study modes
VALID_MODES = {"ask", "explain", "quiz", "summarize", "tips"}

# Base educational guidelines shared across all personas
BASE_INSTRUCTION = (
    "You are Study Buddy, an expert, encouraging AI learning companion for students.\n"
    "Core Guidelines:\n"
    "- Always reply in clean, well-formatted GitHub-flavoured Markdown.\n"
    "- Detect and respond in the language the student writes in (English, Urdu, or Roman Urdu).\n"
    "- Keep content strictly academic and educational. If the student asks about unrelated topics, "
    "politely redirect them back to their studies."
)

# Phase 3: Prompt engineering personas for each study mode
MODE_PROMPTS = {
    "ask": (
        f"{BASE_INSTRUCTION}\n"
        "Persona: Friendly Peer Tutor.\n"
        "Instructions:\n"
        "1. Provide a clear, accurate, and concise answer tailored for beginner-to-intermediate learners.\n"
        "2. Define any technical or unfamiliar term clearly upon first mention.\n"
        "3. Conclude with exactly ONE thoughtful follow-up question to test the student's understanding."
    ),
    "explain": (
        f"{BASE_INSTRUCTION}\n"
        "Persona: The Feynman Technique Mentor (Explain Like I'm 10).\n"
        "Instructions:\n"
        "1. Explain the concept using vivid, relatable everyday real-world analogies.\n"
        "2. Avoid confusing jargon. If a domain term is necessary, immediately explain it in plain English.\n"
        "3. Finish your response with a one-sentence takeaway starting with: '**In short:** ...'."
    ),
    "quiz": (
        f"{BASE_INSTRUCTION}\n"
        "Persona: Interactive Study Quizmaster.\n"
        "Instructions:\n"
        "1. Create exactly 3 multiple-choice questions (options A, B, C, D) of increasing difficulty (Easy, Medium, Challenging).\n"
        "2. Do NOT disclose the correct answers in the questions section.\n"
        "3. Place the answer key and a 1-line explanation per question inside this exact HTML details spoiler block:\n"
        "<details>\n<summary>Click to reveal answers</summary>\n\n"
        "- **Q1: [Option]** - [Brief explanation]\n"
        "- **Q2: [Option]** - [Brief explanation]\n"
        "- **Q3: [Option]** - [Brief explanation]\n"
        "</details>"
    ),
    "summarize": (
        f"{BASE_INSTRUCTION}\n"
        "Persona: Academic Note Synthesizer.\n"
        "Instructions:\n"
        "Organize the student's provided notes or topic into exactly these three distinct sections:\n"
        "### 💡 Core Concept\n"
        "A crisp 1-2 sentence overview of the central idea.\n\n"
        "### 📌 Key Takeaways\n"
        "3 to 5 clear, high-yield bullet points.\n\n"
        "### ⚠️ Common Pitfalls\n"
        "2 to 3 frequent mistakes or misunderstandings students have about this topic."
    ),
    "tips": (
        f"{BASE_INSTRUCTION}\n"
        "Persona: High-Performance Learning Coach.\n"
        "Instructions:\n"
        "Provide actionable, evidence-based study strategies for this topic organized as:\n"
        "### 🧠 Active Recall Prompts\n"
        "3 high-yield questions the student should test themselves with without looking at notes.\n\n"
        "### 📅 Spaced Repetition Schedule\n"
        "A clear timeline (Day 1, Day 3, Day 7, Day 14) for spaced review sessions.\n\n"
        "### ✍️ Practice Exercise\n"
        "One concrete practice task or application scenario.\n\n"
        "### 🎯 Exam-Day Advice\n"
        "One specific, practical tip for answering questions on this topic under exam conditions."
    ),
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("study_buddy")

app = Flask(__name__)


def get_gemini_client() -> genai.Client | None:
    """Initialize and return the Gemini client if an API key is configured."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        return None
    return genai.Client(
        api_key=api_key.strip(),
        http_options={"timeout": 12000}
    )


def generate_demo_response(prompt: str, mode: str = "ask") -> str:
    """Return a rich student-oriented demo response tailored to the selected mode."""
    if mode == "explain":
        return (
            f"### 💡 Explaining: {prompt}\n\n"
            f"Imagine you are explaining this to a 10-year-old friend! Think of **{prompt}** "
            "like a busy kitchen in a popular restaurant: each chef has a single job, recipes are followed step-by-step, "
            "and all the ingredients work together to make a delicious meal.\n\n"
            "Whenever someone talks about this concept, they simply mean organizing complex parts into simple, reliable rules.\n\n"
            f"**In short:** {prompt} is just nature's way of turning raw inputs into useful results through structured teamwork!"
        )
    elif mode == "quiz":
        return (
            f"### 📝 Practice Quiz: {prompt}\n\n"
            f"**1. (Easy)** What is the primary purpose or foundation of {prompt}?\n"
            "   - A) To create chaos\n"
            "   - B) To provide a structured mechanism for energy or information transfer\n"
            "   - C) To stop all physical reactions\n"
            "   - D) None of the above\n\n"
            f"**2. (Medium)** Which component plays the most crucial role in {prompt}?\n"
            "   - A) Catalysts and energy carriers\n"
            "   - B) Random static noise\n"
            "   - C) Inert insulation\n"
            "   - D) Complete equilibrium\n\n"
            f"**3. (Challenging)** How would an external temperature spike most likely alter {prompt}?\n"
            "   - A) It has zero measurable effect\n"
            "   - B) It accelerates rates until denaturation or saturation occurs\n"
            "   - C) It permanently freezes the system\n"
            "   - D) It reverses the direction of time\n\n"
            "<details>\n"
            "<summary>Click to reveal answers</summary>\n\n"
            "- **Q1: B** - Core foundation involves systematic energy or information exchange.\n"
            "- **Q2: A** - Active components and energy carriers drive the main transformation.\n"
            "- **Q3: B** - Thermal energy increases reaction kinetics until optimal limits are breached.\n"
            "</details>"
        )
    elif mode == "summarize":
        return (
            f"### 💡 Core Concept\n"
            f"**{prompt}** is a fundamental process governing how systems interact, transform inputs, and maintain balance.\n\n"
            "### 📌 Key Takeaways\n"
            "- **Foundation:** Starts with primary triggers that initiate sequential reactions.\n"
            "- **Mechanism:** Relies on dedicated pathways to convert energy and process data.\n"
            "- **Significance:** Essential for mastering exam questions on related scientific and logical concepts.\n\n"
            "### ⚠️ Common Pitfalls\n"
            "- Confusing cause with correlation in early phase transitions.\n"
            "- Overlooking boundary conditions and environmental dependencies."
        )
    elif mode == "tips":
        return (
            f"### 🧠 Active Recall Prompts for {prompt}\n"
            "1. Can you explain the 3 main stages from memory without checking your book?\n"
            "2. What formula or principle directly governs this behavior?\n"
            "3. If one variable doubles, what happens to the rest of the equation?\n\n"
            "### 📅 Spaced Repetition Schedule\n"
            "- **Day 1:** Initial deep-dive + write out flashcards.\n"
            "- **Day 3:** 10-minute self-test on tricky terminology.\n"
            "- **Day 7:** Solve 3 past-paper questions without notes.\n"
            "- **Day 14:** Final speed review before exam day.\n\n"
            "### ✍️ Practice Exercise\n"
            f"Draw a simple 1-page diagram illustrating how {prompt} works from start to finish.\n\n"
            "### 🎯 Exam-Day Advice\n"
            "Underline keywords in the question and write down key formulas in the margin right away."
        )
    else:  # default "ask"
        return (
            f"### 💬 Peer Tutor Answer: {prompt}\n\n"
            f"Great question! When studying **{prompt}**, the key idea to grasp is how the underlying mechanism "
            "operates step-by-step. Break it into three parts: inputs, transformation, and final outputs.\n\n"
            "**Key Term:** *Equilibrium* — a balanced state where forward and reverse actions happen at identical rates.\n\n"
            "**Check Your Understanding:** Can you tell me what you think happens if one of the initial inputs is removed?"
        )


@app.route("/", methods=["GET"])
def index():
    """Render the Study Buddy web application."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint: returns app name, status, model, and supported modes."""
    api_key = os.getenv("GEMINI_API_KEY")
    gemini_connected = bool(api_key and api_key.strip())

    return jsonify({
        "app": "Study Buddy",
        "status": "healthy",
        "gemini_connected": gemini_connected,
        "model": GEMINI_MODEL,
        "supported_modes": sorted(list(VALID_MODES)),
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint: accepts a prompt and mode, returns persona-guided AI or demo response."""
    # Validate request payload
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request body. JSON payload is required."
        }), 400

    prompt = data.get("prompt")
    if prompt is None or not isinstance(prompt, str) or not prompt.strip():
        return jsonify({
            "error": "The 'prompt' field is required and cannot be empty."
        }), 400

    mode = data.get("mode", "ask")
    if not isinstance(mode, str) or mode not in VALID_MODES:
        return jsonify({
            "error": f"Invalid mode '{mode}'. Allowed modes are: {', '.join(sorted(VALID_MODES))}."
        }), 400

    clean_prompt = prompt.strip()
    system_instruction = MODE_PROMPTS.get(mode, MODE_PROMPTS["ask"])

    # Check for API key / client
    client = get_gemini_client()
    if client is None:
        logger.warning("GEMINI_API_KEY is missing or empty. Falling back to demo mode.")
        return jsonify({
            "response": generate_demo_response(clean_prompt, mode=mode),
            "source": "demo",
            "note": "GEMINI_API_KEY is missing or not configured in .env. Returning demo response."
        }), 200

    # Attempt Gemini API call with prompt-engineered system instruction
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
    )

    try:
        logger.info("Calling Gemini API with model '%s' for mode '%s'...", GEMINI_MODEL, mode)
        gemini_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=clean_prompt,
            config=config,
        )

        response_text = gemini_response.text or ""
        return jsonify({
            "response": response_text,
            "source": "gemini"
        }), 200

    except Exception as primary_err:
        logger.warning(
            "Primary model '%s' failed (%s). Attempting stable fallback model '%s'...",
            GEMINI_MODEL, primary_err, FALLBACK_MODEL
        )
        
        # Automatic fallback to stable model if gemini-3.8-flash has a 504 deadline / 503 spike
        if GEMINI_MODEL != FALLBACK_MODEL:
            try:
                gemini_response = client.models.generate_content(
                    model=FALLBACK_MODEL,
                    contents=clean_prompt,
                    config=config,
                )
                response_text = gemini_response.text or ""
                return jsonify({
                    "response": response_text,
                    "source": "gemini"
                }), 200
            except Exception as fallback_err:
                logger.error("Fallback model '%s' also failed: %s", FALLBACK_MODEL, fallback_err, exc_info=True)
                err = fallback_err
        else:
            err = primary_err

        return jsonify({
            "response": generate_demo_response(clean_prompt, mode=mode),
            "source": "demo",
            "note": f"Gemini API call failed ({type(err).__name__}: {str(err)}). Falling back to demo response."
        }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info("Starting Study Buddy on port %d with model '%s'...", port, GEMINI_MODEL)
    app.run(host="0.0.0.0", port=port, debug=False)
