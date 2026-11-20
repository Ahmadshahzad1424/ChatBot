import logging
import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# Gemini model constant at top of file, overridable with GEMINI_MODEL env var
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

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
    return genai.Client(api_key=api_key.strip())


def generate_demo_response(prompt: str) -> str:
    """Return a helpful student-oriented demo response when Gemini is unavailable."""
    return (
        f"Hello! I am Study Buddy, your AI study assistant (Demo Mode).\n\n"
        f"You asked: \"{prompt}\"\n\n"
        "Here is a quick study tip: Break complex topics into smaller chunks, "
        "use active recall, and apply the Pomodoro technique (25 min focus, 5 min break). "
        "Once a valid GEMINI_API_KEY is configured in your .env file, I will provide full AI-powered answers!"
    )


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint: returns app name, status, and Gemini connection state."""
    api_key = os.getenv("GEMINI_API_KEY")
    gemini_connected = bool(api_key and api_key.strip())

    return jsonify({
        "app": "Study Buddy",
        "status": "healthy",
        "gemini_connected": gemini_connected,
        "model": GEMINI_MODEL,
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint: accepts a prompt and returns an AI or demo response."""
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

    clean_prompt = prompt.strip()

    # Check for API key / client
    client = get_gemini_client()
    if client is None:
        logger.warning("GEMINI_API_KEY is missing or empty. Falling back to demo mode.")
        return jsonify({
            "response": generate_demo_response(clean_prompt),
            "source": "demo",
            "note": "GEMINI_API_KEY is missing or not configured in .env. Returning demo response."
        }), 200

    # Attempt Gemini API call
    try:
        logger.info("Calling Gemini API with model '%s'...", GEMINI_MODEL)
        gemini_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=clean_prompt,
        )

        response_text = gemini_response.text or ""
        return jsonify({
            "response": response_text,
            "source": "gemini"
        }), 200

    except Exception as err:
        logger.error("Gemini API call failed: %s", err, exc_info=True)
        return jsonify({
            "response": generate_demo_response(clean_prompt),
            "source": "demo",
            "note": f"Gemini API call failed ({type(err).__name__}: {str(err)}). Falling back to demo response."
        }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info("Starting Study Buddy on port %d with model '%s'...", port, GEMINI_MODEL)
    app.run(host="0.0.0.0", port=port, debug=False)
