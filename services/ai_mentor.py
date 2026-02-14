"""AI Mentor using Gemini API: reasoning, suggestions, Q&A."""
from typing import Optional

from config import GEMINI_API_KEY

# Cache discovered model name so we don't list on every request
_CACHED_MODEL_NAME: Optional[str] = None


def list_available_models() -> list[str]:
    """List model names that support generateContent (for debugging)."""
    if not GEMINI_API_KEY:
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        out = []
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                name = getattr(m, "name", None) or ""
                if name.startswith("models/"):
                    name = name.replace("models/", "", 1)
                out.append(name)
        return out
    except Exception:
        return []


def _get_model_name(genai) -> str:
    """Find a model that supports generateContent for this API key."""
    global _CACHED_MODEL_NAME
    if _CACHED_MODEL_NAME:
        return _CACHED_MODEL_NAME
    try:
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                # m.name is like "models/gemini-1.5-flash" - use as-is or strip "models/"
                name = getattr(m, "name", None) or ""
                if name.startswith("models/"):
                    name = name.replace("models/", "", 1)
                _CACHED_MODEL_NAME = name
                return _CACHED_MODEL_NAME
    except Exception:
        pass
    # Fallbacks if list_models fails or returns nothing
    for fallback in ("gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"):
        _CACHED_MODEL_NAME = fallback
        return fallback


def get_mentor_response(
    insight_summary: dict,
    user_question: Optional[str] = None,
    student_id: Optional[str] = None,
) -> str:
    """Call Gemini with performance context; optional Q&A."""
    if not GEMINI_API_KEY:
        return "AI Mentor is not configured. Please set GEMINI_API_KEY in .env."

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        return f"Failed to initialize Gemini: {e}"

    model_name = _get_model_name(genai)
    model = genai.GenerativeModel(model_name)

    summary = insight_summary.get("summary", {})
    students = insight_summary.get("students", [])
    correlation_text = summary.get("attendance_marks_correlation", "")

    def _student_block(s: dict) -> str:
        # Format subject marks for chart analysis
        sub_marks = s.get('subject_marks', [])
        sub_str = ", ".join([f"{m['subject']}: {m['marks']}" for m in sub_marks]) if sub_marks else "No specific subject data."
        
        return (
            f"Name: {s.get('name')}. "
            f"Average marks: {s.get('avg_marks')}. "
            f"Attendance: {s.get('attendance_avg')}%. "
            f"Academic health score: {s.get('academic_health')}. "
            f"Subject Marks (Chart Data): [{sub_str}]. "
            f"Weak subjects: {s.get('weak_subjects', [])}. "
            f"Focus areas: {s.get('risk_flags', [])}."
        )

    student_context = ""
    if student_id:
        for s in students:
            if str(s.get("student_id")) == str(student_id):
                # Ensure subject_marks is present if not already
                if "subject_marks" not in s: 
                     # Fallback or re-fetch if needed, but usually analytics provides it.
                     pass 
                student_context = "Focus on this student.\n" + _student_block(s)
                break
    if not student_context:
        student_context = (
            f"Overall: {summary.get('total_students')} students, "
            f"{summary.get('students_at_risk_count')} need support. "
            f"Key insight: {correlation_text}. "
            "Student data:\n" + "\n".join(_student_block(s) for s in students[:15])
        )
    else:
        student_context += f"\nKey insight for everyone: {correlation_text}"

    system_role = (
        "You are a supportive Personal Study Coach. Use only the data provided. "
        "Always be encouraging and use supportive language. "
        "Format your response using Markdown. Use bolding for key terms. "
        "Use numbered lists for steps. "
        "Do not use harsh labels; use terms like 'focus areas' and 'room to grow'.\n\n"
        "**CHARTS:** If helpful for comparison or visualizing trends, generate a chart using this JSON format inside a code block with language 'chart'.\n"
        "IMPORTANT: The code block must contain ONLY valid JSON. Do not add comments or text inside the block.\n"
        "```chart\n"
        "{\"type\": \"bar\", \"title\": \"Chart Title\", \"labels\": [\"Subject A\", \"Subject B\"], \"data\": [80, 90]}\n"
        "```\n"
        "Supported types: 'doughnut', 'bar', 'pie', 'line'. Use 'bar' for subject comparison."
    )
    if user_question:
        prompt = (
            system_role + "\n\nData:\n" + student_context + "\n\n"
            "Student's question: " + user_question + "\n\n"
            "Reply with:\n"
            "1. A brief personalized explanation\n"
            "2. **Concrete actionable steps** (formatted as a numbered list)\n"
            "3. An encouraging closing."
        )
    else:
        prompt = (
            system_role + "\n\nData:\n" + student_context + "\n\n"
            "Give a short performance overview.\n"
            "Then list 2–3 concrete, actionable improvement steps formatted as a numbered list.\n"
            "End with one encouraging sentence."
        )

    # Retry with another model if we get 404 (model not found)
    global _CACHED_MODEL_NAME
    fallbacks = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    models_to_try = [model_name] + [f for f in fallbacks if f != model_name]
    last_error = None
    for m_name in models_to_try:
        try:
            m = genai.GenerativeModel(m_name)
            response = m.generate_content(prompt)
            if response and response.text:
                return response.text
            last_error = "No response from AI."
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "not found" in err_str.lower():
                last_error = e
                _CACHED_MODEL_NAME = None  # force re-list next time
                continue
            return f"AI error: {e}"
    return f"AI error: {last_error}"
