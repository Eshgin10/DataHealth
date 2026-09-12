import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db, Job
from backend.services.processor import process_csv

router = APIRouter()

UPLOAD_DIR = "uploads/raw"

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    if file.size is not None and file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV files must be 20 MB or smaller")

    job_id = str(uuid.uuid4())
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    new_job = Job(id=job_id, filename=file.filename, status="uploading")
    db.add(new_job)
    db.commit()
    
    # Trigger background processing
    background_tasks.add_task(process_csv, job_id, file_path)
    
    return {"job_id": job_id, "filename": file.filename, "status": "uploading"}

@router.get("/sample")
async def get_sample():
    sample_path = "sample-data/customer_data_raw.csv"
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="Sample dataset not found")
    return FileResponse(sample_path, media_type="text/csv", filename="customer_data_raw.csv")
