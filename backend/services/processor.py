import json
import traceback
import pandas as pd
from backend.database import SessionLocal, Job, ColumnProfile, Issue
from backend.profiling.engine import profile_dataframe


def process_csv(job_id: str, file_path: str):
    """Background task that profiles, validates, and scores a CSV."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        # ── Step 1: Profiling ──
        job.status = "profiling"
        db.commit()

        df = pd.read_csv(file_path, low_memory=False)
        job.row_count = len(df)
        job.col_count = len(df.columns)
        db.commit()

        db.query(ColumnProfile).filter(ColumnProfile.job_id == job_id).delete()
        db.query(Issue).filter(Issue.job_id == job_id).delete()
        profiles = profile_dataframe(df)
        for col, prof in profiles.items():
            cp = ColumnProfile(
                job_id=job_id,
                name=col,
                semantic_type=prof["type"],
                null_count=prof["null_count"],
                null_pct=prof["null_pct"],
                unique_count=prof["unique_count"],
                unique_pct=prof["unique_pct"],
                min_val=prof.get("min"),
                max_val=prof.get("max"),
                mean_val=prof.get("mean"),
                most_common=json.dumps(prof.get("most_common", {})),
            )
            db.add(cp)
        db.commit()

        # ── Step 2: Validation ──
        job.status = "validating"
        db.commit()

        from backend.validators.engine import validate_dataframe

        issues_list = validate_dataframe(df, profiles)
        for iss in issues_list:
            db.add(
                Issue(
                    job_id=job_id,
                    category=iss["category"],
                    column_name=iss["column_name"],
                    issue_type=iss["issue_type"],
                    severity=iss["severity"],
                    affected_rows=iss["affected_rows"],
                )
            )
        db.commit()

        # ── Step 3: Scoring ──
        total_cells = job.row_count * job.col_count if job.row_count and job.col_count else 1
        missing_issues = sum(
            i["affected_rows"]
            for i in issues_list
            if i["category"] == "MISSING DATA"
        )
        invalid_issues = sum(
            i["affected_rows"]
            for i in issues_list
            if i["category"]
            in ["INVALID VALUES", "NUMERIC ANOMALIES", "LOGICAL CONFLICTS"]
        )
        consistency_issues = sum(
            i["affected_rows"]
            for i in issues_list
            if i["category"]
            in ["CATEGORICAL INCONSISTENCIES", "WHITESPACE / CASE ISSUES"]
        )
        duplicate_issues = sum(
            i["affected_rows"]
            for i in issues_list
            if i["category"] == "DUPLICATES"
        )

        completeness = max(0.0, 100.0 * (1 - missing_issues / total_cells))
        validity = max(0.0, 100.0 * (1 - invalid_issues / total_cells))
        consistency = max(0.0, 100.0 * (1 - consistency_issues / total_cells))
        uniqueness = max(
            0.0,
            100.0 * (1 - duplicate_issues / job.row_count)
            if job.row_count
            else 100.0,
        )

        job.completeness_score = round(completeness, 1)
        job.validity_score = round(validity, 1)
        job.consistency_score = round(consistency, 1)
        job.uniqueness_score = round(uniqueness, 1)

        job.health_score = round(
            completeness * 0.25
            + validity * 0.30
            + consistency * 0.20
            + uniqueness * 0.15
            + 100 * 0.10,
            1,
        )

        job.status = "done"
        db.commit()
        print(f"[OK] Job {job_id} processed successfully. Score: {job.health_score}")

    except Exception:
        db.rollback()
        tb = traceback.format_exc()
        print(f"[ERROR] Job {job_id} failed:\n{tb}")
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "error"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
