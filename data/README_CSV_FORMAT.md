# CSV format for Student Performance Analysis

Use this format so your upload works without errors.

## Required columns (exact or accepted names)

| Use this (or accepted name) | Description | Example |
|-----------------------------|-------------|---------|
| **student_id** (or `Student ID`, `studentid`) | Unique ID per student | S001, 1, 101 |
| **subject** (or `Subject`, `Course`) | Subject/course name | Mathematics, Physics |
| **marks** (or `Marks`, `Score`, `scores`) | Numeric score 0–100 | 72, 85 |

## Optional columns (recommended)

| Column | Accepted names | Description |
|--------|----------------|-------------|
| **name** | Name, Student name | Student full name |
| **attendance_pct** | Attendance, Attendance %, attendance_pct | 0–100 |
| **grade** | Grade, letter grade | A, B+, C |
| **semester** | Semester, Sem, Term | 1, 2 |

## Format rules

- First row must be the header (column names).
- One row per subject per student (e.g. same student has multiple rows for Math, Physics, etc.).
- Save the file as **UTF-8** CSV (Excel: “CSV UTF-8 (Comma delimited)”).
- Use commas to separate columns.

## Template

Copy `dataset_template.csv` in this folder as a starting point, or use the sample:

```
student_id,name,subject,marks,attendance_pct,grade,semester
S001,Alice,Mathematics,72,88,B+,1
S001,Alice,Physics,65,82,B,1
S002,Bob,Mathematics,88,92,A,1
```

Then replace with your own student IDs, names, subjects, and marks.
