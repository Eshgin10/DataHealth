from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, Job, ColumnProfile, Issue
import json

router = APIRouter()

def serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "filename": job.filename,
        "status": job.status,
        "row_count": job.row_count or 0,
        "col_count": job.col_count or 0,
        "health_score": job.health_score or 0.0,
        "completeness_score": job.completeness_score or 0.0,
        "validity_score": job.validity_score or 0.0,
        "consistency_score": job.consistency_score or 0.0,
        "uniqueness_score": job.uniqueness_score or 0.0,
        "created_at": str(job.created_at) if job.created_at else None,
        "updated_at": str(job.updated_at) if job.updated_at else None,
    }

def serialize_issue(issue: Issue) -> dict:
    return {
        "id": issue.id,
        "job_id": issue.job_id,
        "category": issue.category,
        "column_name": issue.column_name,
        "issue_type": issue.issue_type,
        "severity": issue.severity,
        "affected_rows": issue.affected_rows,
        "status": issue.status,
    }

@router.get("/jobs")
async def list_jobs(db: Session = Depends(get_db)):
    return [serialize_job(j) for j in db.query(Job).order_by(Job.created_at.desc()).all()]

@router.get("/jobs/{job_id}")
async def get_job_overview(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    issues_list = db.query(Issue).filter(Issue.job_id == job_id, Issue.status == "open").all()
    total_issues = len(issues_list)
    affected_rows = sum(i.affected_rows for i in issues_list)

    # columns with issues
    cols_with_issues = len(set(i.column_name for i in issues_list if i.column_name))

    return {
        "job": serialize_job(job),
        "metrics": {
            "total_issues": total_issues,
            "affected_rows": affected_rows,
            "columns_with_issues": cols_with_issues,
        },
    }

@router.get("/jobs/{job_id}/columns")
async def get_job_columns(job_id: str, db: Session = Depends(get_db)):
    columns = db.query(ColumnProfile).filter(ColumnProfile.job_id == job_id).all()
    result = []
    for c in columns:
        cdict = {
            "name": c.name,
            "semantic_type": c.semantic_type,
            "null_count": c.null_count,
            "null_pct": c.null_pct,
            "unique_count": c.unique_count,
            "unique_pct": c.unique_pct,
            "min_val": c.min_val,
            "max_val": c.max_val,
            "mean_val": c.mean_val,
            "most_common": json.loads(c.most_common) if c.most_common else {},
        }
        result.append(cdict)
    return result

@router.get("/jobs/{job_id}/issues")
async def get_job_issues(job_id: str, db: Session = Depends(get_db)):
    issues = db.query(Issue).filter(Issue.job_id == job_id).all()
    return [serialize_issue(i) for i in issues]
