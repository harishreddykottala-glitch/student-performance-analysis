"""Insight generator: structured performance summary and risk flags."""
from typing import Any


def _correlation_interpretation(r_val: float) -> str:
    """Student-friendly interpretation of attendance–marks correlation (no raw numbers)."""
    if r_val >= 0.7:
        return "Attendance has a very strong impact on your performance 📈"
    if r_val >= 0.4:
        return "Attendance is linked to better performance — showing up helps 📚"
    if r_val >= 0.2:
        return "Attendance shows some link to performance"
    if r_val >= -0.2:
        return "Attendance and marks show a mild relationship"
    return "Consider focusing on both attendance and study habits"


def _friendly_risk_flags(r: dict) -> list[str]:
    """Supportive language for risk flags."""
    flags = []
    # Check directly against values for robustness
    avg = r.get("avg_marks", 0)
    att = r.get("attendance_avg", 0)
    
    if avg < 60:
        flags.append("Needs academic attention")
    elif avg < 70:
        flags.append("Room for improvement")
        
    if att is not None and att < 75:
        flags.append("Attendance improvement needed")
        
    weak_count = r.get("weak_subject_count", 0)
    if weak_count >= 1:
        # List specific weak subjects if few, else generic message
        subs = r.get("weak_subjects", [])
        if subs and len(subs) <= 2:
            flags.append(f"Focus: {', '.join(subs)}")
        else:
            flags.append("Multiple focus areas")
            
    return flags


def build_insight_summary(analytics: dict[str, Any]) -> dict[str, Any]:
    """Turn analytics output into a structured performance summary and risk flags."""
    risk_list = analytics.get("risk_analysis", [])
    avg_list = analytics.get("average_marks", [])
    corr = analytics.get("attendance_correlation", {})

    students_summary = []
    for r in risk_list:
        sid = r.get("student_id", "")
        avg_m = r.get("avg_marks") or 0
        att = r.get("attendance_avg")
        att_pct = att if att is not None else 0
        # academic_health = 0.6 * average_marks + 0.4 * attendance_percentage (0–100)
        academic_health = round(0.6 * avg_m + 0.4 * att_pct, 1)
        students_summary.append({
            "student_id": sid,
            "name": r.get("name", ""),
            "avg_marks": r.get("avg_marks"),
            "attendance_avg": r.get("attendance_avg"),
            "academic_health": academic_health,
            "weak_subjects": r.get("weak_subjects", []),
            "subject_marks": r.get("subject_marks", []),
            "risk_flags": _friendly_risk_flags(r),
        })

    overall_corr = corr.get("overall") if isinstance(corr, dict) else None
    correlation_interpretation = "N/A"
    if overall_corr and "correlation" in overall_corr:
        r_val = overall_corr["correlation"]
        correlation_interpretation = _correlation_interpretation(r_val)

    # Class-level average academic health for hero meter (when no student selected)
    class_health = 0.0
    if students_summary:
        class_health = round(
            sum(s["academic_health"] for s in students_summary) / len(students_summary), 1
        )

    return {
        "summary": {
            "total_students": len(avg_list),
            "attendance_marks_correlation": correlation_interpretation,
            "students_at_risk_count": sum(1 for r in risk_list if (
                r.get("risk_low_marks") or r.get("risk_low_attendance") or r.get("risk_multiple_weak")
            )),
            "class_academic_health": class_health,
        },
        "students": students_summary,
        "raw_analytics": analytics,
    }
