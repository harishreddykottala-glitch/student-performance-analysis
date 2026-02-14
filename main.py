"""Backend API: request handling, data + AI integration."""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import SAMPLE_CSV
from services.ingestion import load_csv, preprocess, save_upload
from services.analytics import run_analytics
from services.insights import build_insight_summary
from services.ai_mentor import get_mentor_response, list_available_models

app = FastAPI(title="Student Performance Analysis", version="1.0.0")


class ChatRequest(BaseModel):
    question: str
    student_id: Optional[str] = None
    filename: Optional[str] = None


# Load and cache insights for default sample data
def _get_insights(csv_path: Optional[Path] = None):
    df = load_csv(csv_path)
    analytics = run_analytics(df)
    return build_insight_summary(analytics)


@app.get("/")
async def root():
    """Serve dashboard."""
    index = Path(__file__).parent / "static" / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Student Performance API", "docs": "/docs"}


@app.get("/api/insights")
async def api_insights(csv_path: Optional[str] = None):
    """Get full insights (summary + students + analytics). Uses sample CSV if no path."""
    try:
        path = Path(csv_path) if csv_path else None
        insights = _get_insights(path)
        return insights
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    """Upload a CSV and return insights for it."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV file required")
    try:
        content = await file.read()
        path = save_upload(content, file.filename)
        insights = _get_insights(path)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mentor/models")
async def api_mentor_models():
    """List Gemini models available for your API key (for debugging)."""
    return {"models": list_available_models()}


@app.get("/api/mentor")
async def api_mentor_summary():
    """AI mentor overview (no question)."""
    insights = _get_insights(None)
    text = get_mentor_response(insights, user_question=None, student_id=None)
    return {"response": text}


@app.post("/api/mentor/chat")
async def api_mentor_chat(body: ChatRequest):
    """AI mentor Q&A with optional student focus."""
    # Use uploaded file if specified, else default
    csv_path = None
    if body.filename:
        # Sanitize filename to prevent directory traversal
        safe_name = Path(body.filename).name
        possible_path = Path("data/uploads") / safe_name
        if possible_path.exists():
            csv_path = possible_path

    insights = _get_insights(csv_path)
    text = get_mentor_response(
        insights,
        user_question=body.question,
        student_id=body.student_id,
    )
    return {"response": text}


# Static files for dashboard
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
