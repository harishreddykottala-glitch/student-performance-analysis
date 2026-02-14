"""Data ingestion and preprocessing (cleaning, formatting)."""
import pandas as pd
from pathlib import Path
from typing import Optional

from config import UPLOAD_DIR, SAMPLE_CSV

# Map common CSV header variants to our expected column names (lowercase for match)
COLUMN_ALIASES = {
    "student_id": ["student id", "studentid", "student_id", "id", "student"],
    "name": ["name", "student name", "studentname", "student_name"],
    "subject": ["subject", "subjects", "course", "course name"],
    "marks": ["marks", "mark", "score", "scores", "grade score", "total", "total marks"],
    "attendance_pct": ["attendance_pct", "attendance", "attendance %", "attendance%", "attendance_pct", "attendance percent", "attendance_percentage"],
    "grade": ["grade", "grades", "letter grade"],
    "semester": ["semester", "sem", "term"],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map common column names to expected names (student_id, name, subject, marks, attendance_pct, etc.)."""
    df = df.copy()
    new_names = {}
    for col in df.columns:
        c = str(col).strip()
        c_lower = c.lower()
        if c_lower in [k.lower() for k in COLUMN_ALIASES.keys()]:
            continue  # already canonical
        for canonical, aliases in COLUMN_ALIASES.items():
            if c_lower in [a.lower() for a in aliases]:
                if canonical not in new_names.values() and canonical not in df.columns:
                    new_names[col] = canonical
                break
    if new_names:
        df = df.rename(columns=new_names)
    return df


def load_csv(path: Optional[Path] = None) -> pd.DataFrame:
    """Load student CSV from path or use sample."""
    p = path or SAMPLE_CSV
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {p}")
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(p, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not read CSV: unsupported encoding. Try saving as UTF-8.")
    # If only one column, try semicolon or tab
    if len(df.columns) < 2 and len(df) > 0:
        for sep in (";", "\t"):
            try:
                df = pd.read_csv(p, encoding=encoding, sep=sep)
                if len(df.columns) >= 2:
                    break
            except Exception:
                pass
    df = _normalize_columns(df)
    return preprocess(df)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize: types, nulls, valid ranges."""
    df = df.copy()
    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    # Ensure we have required columns (after alias mapping)
    required = ["student_id", "subject", "marks"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            "Expected headers like: student_id (or 'Student ID'), subject, marks (or 'Marks'/'Score')."
        )
    # Numeric columns
    if "marks" in df.columns:
        df["marks"] = pd.to_numeric(df["marks"], errors="coerce").clip(0, 100)
    if "attendance_pct" in df.columns:
        df["attendance_pct"] = pd.to_numeric(df["attendance_pct"], errors="coerce").clip(0, 100)
    if "semester" in df.columns:
        df["semester"] = pd.to_numeric(df["semester"], errors="coerce").fillna(1).astype(int)
    # Drop rows with critical nulls
    for c in required:
        df = df.dropna(subset=[c])
    if df.empty:
        raise ValueError(
            "No valid rows after reading CSV. Check that student_id, subject, and marks columns have values."
        )
    return df.reset_index(drop=True)


def save_upload(file_content: bytes, filename: str) -> Path:
    """Save uploaded file to data/uploads and return path."""
    path = UPLOAD_DIR / filename
    path.write_bytes(file_content)
    return path
