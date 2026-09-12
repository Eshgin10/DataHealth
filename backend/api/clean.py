from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db, Job, Issue
import pandas as pd
import os

router = APIRouter()

@router.post("/jobs/{job_id}/clean")
async def apply_cleaning(
    job_id: str,
    action: str = Query(...),
    column: str = Query(None),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    raw_path = f"uploads/raw/{job_id}.csv"
    clean_path = f"uploads/clean/{job_id}.csv"

    # Read from clean path if it exists (iterative cleaning), else raw
    path_to_read = clean_path if os.path.exists(clean_path) else raw_path
    if not os.path.exists(path_to_read):
        raise HTTPException(status_code=404, detail="File not found")

    df = pd.read_csv(path_to_read)

    affected_rows = 0

    if action == "trim_whitespace" and column and column in df.columns:
        s_str = df[column].astype("string")
        s_stripped = s_str.str.strip()
        affected_rows = int((s_str != s_stripped).sum())
        df[column] = s_stripped

    elif action == "normalize_casing" and column and column in df.columns:
        s_str = df[column].astype("string")
        s_titled = s_str.str.strip().str.title()
        affected_rows = int((s_str != s_titled).sum())
        df[column] = s_titled

    elif action == "remove_duplicates":
        before = len(df)
        df = df.drop_duplicates()
        affected_rows = before - len(df)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    # Save back to clean path
    os.makedirs("uploads/clean", exist_ok=True)
    df.to_csv(clean_path, index=False)

    # Update issue status in DB
    if action == "trim_whitespace":
        issues = (
            db.query(Issue)
            .filter(
                Issue.job_id == job_id,
                Issue.column_name == column,
                Issue.issue_type == "leading or trailing whitespace",
            )
            .all()
        )
    elif action == "normalize_casing":
        issues = (
            db.query(Issue)
            .filter(
                Issue.job_id == job_id,
                Issue.column_name == column,
                Issue.issue_type == "case inconsistencies",
            )
            .all()
        )
    elif action == "remove_duplicates":
        issues = (
            db.query(Issue)
            .filter(Issue.job_id == job_id, Issue.issue_type == "exact duplicates")
            .all()
        )
    else:
        issues = []

    for i in issues:
        i.status = "fixed"
    db.commit()

    from backend.services.processor import process_csv
    process_csv(job_id, clean_path)

    return {"status": "success", "action": action, "affected_rows": affected_rows}


@router.get("/jobs/{job_id}/download/cleaned")
async def download_cleaned(job_id: str, db: Session = Depends(get_db)):
    clean_path = f"uploads/clean/{job_id}.csv"
    raw_path = f"uploads/raw/{job_id}.csv"

    # If no cleaning has been done yet, serve the raw file
    path = clean_path if os.path.exists(clean_path) else raw_path
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    return FileResponse(path, media_type="text/csv", filename="cleaned_dataset.csv")
