import json
import time
import google.generativeai as genai
from app.core.config import get_settings

CLIMBING_ANALYSIS_PROMPT = """You are an expert climbing coach analyzing a bouldering video.
Analyze the climber's form and provide:
1. Overall form feedback (1-2 sentences)
2. Grade estimate (e.g. V4, V5)
3. Body position analysis: posture, tension, efficiency score (0-10)
4. Holds analysis: for each key hold, position, type, and quality of interaction
5. Top 3 key weaknesses to improve

Return ONLY valid JSON with these exact keys:
{
  "form_feedback": "string",
  "grade_estimate": "string",
  "body_position": {"posture": "string", "tension": "string", "efficiency_score": number},
  "holds_analysis": [{"position": "string", "type": "string", "quality": "string"}],
  "key_weaknesses": ["string", "string", "string"]
}"""

_configured = False

# Max time to wait for Gemini to process a video file (seconds)
FILE_PROCESSING_TIMEOUT = 300
FILE_PROCESSING_POLL_INTERVAL = 2


def _ensure_configured():
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


async def analyze_climbing_form(video_path: str) -> dict:
    """
    Sends video to Gemini Vision for climbing form analysis using the File API.
    Uploads the entire video once, waits for processing, then makes a single
    generate_content call. NO frame-by-frame extraction.

    Returns parsed dict matching AnalysisResponse schema.
    """
    _ensure_configured()

    # Step 1: Upload entire video to Gemini File API (one upload)
    video_file = genai.upload_file(path=video_path)

    # Step 2: Wait for Gemini to finish processing the video
    elapsed = 0
    while video_file.state.name == "PROCESSING":
        if elapsed >= FILE_PROCESSING_TIMEOUT:
            raise TimeoutError(
                f"Gemini file processing timed out after {FILE_PROCESSING_TIMEOUT}s"
            )
        time.sleep(FILE_PROCESSING_POLL_INTERVAL)
        elapsed += FILE_PROCESSING_POLL_INTERVAL
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise RuntimeError("Gemini file processing failed")

    # Step 3: Single API call — Gemini analyzes the full video internally
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        [video_file, CLIMBING_ANALYSIS_PROMPT],
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    # Parse JSON response
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    result = json.loads(text)

    return {
        "form_feedback": result.get("form_feedback", "Analysis completed"),
        "grade_estimate": result.get("grade_estimate"),
        "body_position": result.get("body_position", {"posture": "unknown", "tension": "unknown", "efficiency_score": 0}),
        "holds_analysis": result.get("holds_analysis", []),
        "key_weaknesses": result.get("key_weaknesses", []),
    }
