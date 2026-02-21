import json
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


def _ensure_configured():
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


async def analyze_climbing_form(video_path: str) -> dict:
    """
    Sends video to Gemini Vision for climbing form analysis.
    Returns parsed dict matching AnalysisResponse schema.
    """
    _ensure_configured()

    model = genai.GenerativeModel("gemini-2.0-flash")

    # Upload video file to Gemini
    video_file = genai.upload_file(video_path)

    response = model.generate_content(
        [CLIMBING_ANALYSIS_PROMPT, video_file],
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    # Parse JSON response
    text = response.text.strip()
    # Handle potential markdown code block wrapping
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    result = json.loads(text)

    # Ensure required keys exist with defaults
    return {
        "form_feedback": result.get("form_feedback", "Analysis completed"),
        "grade_estimate": result.get("grade_estimate"),
        "body_position": result.get("body_position", {"posture": "unknown", "tension": "unknown", "efficiency_score": 0}),
        "holds_analysis": result.get("holds_analysis", []),
        "key_weaknesses": result.get("key_weaknesses", []),
    }
