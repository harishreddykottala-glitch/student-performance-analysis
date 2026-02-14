"""Analytics & ML engine: averages, correlation, weak subjects, risk."""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Any


def average_marks_by_student(df: pd.DataFrame) -> pd.DataFrame:
    """Average marks per student (and overall)."""
    if "student_id" not in df.columns or "marks" not in df.columns:
        return pd.DataFrame()
    agg = df.groupby("student_id").agg(
        avg_marks=("marks", "mean"),
        total_subjects=("subject", "nunique"),
    ).round(2)
    if "name" in df.columns:
        names = df.groupby("student_id")["name"].first()
        agg = agg.assign(name=names)
    return agg.reset_index()


def attendance_correlation(df: pd.DataFrame) -> dict[str, Any]:
    """Correlation between attendance_pct and marks (overall and per subject)."""
    if "attendance_pct" not in df.columns or "marks" not in df.columns:
        return {"overall": None, "by_subject": {}}
    r, p = stats.pearsonr(df["attendance_pct"], df["marks"])
    by_subject = {}
    for subj in df["subject"].dropna().unique():
        s = df[df["subject"] == subj]
        if len(s) >= 3:
            r_s, p_s = stats.pearsonr(s["attendance_pct"], s["marks"])
            by_subject[str(subj)] = {"correlation": round(float(r_s), 4), "p_value": round(float(p_s), 4)}
    return {
        "overall": {"correlation": round(float(r), 4), "p_value": round(float(p), 4)},
        "by_subject": by_subject,
    }


def weak_subjects(df: pd.DataFrame, threshold: float = 50) -> dict[str, list[dict]]:
    """Detect weak subjects per student (marks below threshold)."""
    if "student_id" not in df.columns or "marks" not in df.columns or "subject" not in df.columns:
        return {}
    out = {}
    for sid, g in df.groupby("student_id"):
        weak = g[g["marks"] < threshold][["subject", "marks"]].to_dict("records")
        for r in weak:
            r["marks"] = round(float(r["marks"]), 2)
        out[str(sid)] = weak
    return out


def risk_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Risk flags: low attendance, low average, multiple weak subjects."""
    avg_df = average_marks_by_student(df)
    if avg_df.empty:
        return pd.DataFrame()

    risk_list = []
    for _, row in avg_df.iterrows():
        sid = row["student_id"]
        student_df = df[df["student_id"] == sid]
        avg_m = row["avg_marks"]
        att = student_df["attendance_pct"].mean() if "attendance_pct" in student_df.columns else None
        weak = [s for s in weak_subjects(df, threshold=50).get(str(sid), [])]
        
        # Calculate subject-wise marks for this student
        subject_marks = []
        if "subject" in student_df.columns and "marks" in student_df.columns:
            subject_marks = student_df[["subject", "marks"]].to_dict(orient="records")

        risk_list.append({
            "student_id": sid,
            "name": row.get("name", ""),
            "avg_marks": round(avg_m, 2),
            "attendance_avg": round(float(att), 2) if att is not None and not np.isnan(att) else None,
            "weak_subject_count": len(weak),
            "weak_subjects": [w["subject"] for w in weak],
            "subject_marks": subject_marks,
            "risk_low_marks": avg_m < 55,
            "risk_low_attendance": att is not None and att < 75,
            "risk_multiple_weak": len(weak) >= 2,
        })
    return pd.DataFrame(risk_list)


def run_analytics(df: pd.DataFrame) -> dict[str, Any]:
    """Run full analytics pipeline and return a single dict."""
    return {
        "average_marks": average_marks_by_student(df).to_dict(orient="records"),
        "attendance_correlation": attendance_correlation(df),
        "weak_subjects": weak_subjects(df, threshold=50),
        "risk_analysis": risk_analysis(df).to_dict(orient="records"),
    }
