from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import upload, clean, jobs

app = FastAPI(title="Data Health API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(clean.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Data Health API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
