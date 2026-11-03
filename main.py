
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from database import Base, engine, SessionLocal
from models import Candidate


statuses = [
    "Applied",
    "Screening",
    "Interview",
    "Hired",
    "Rejected"
]

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RecruitFlow ATS",
    lifespan=lifespan
)


@app.get("/")
def dashboard(request: Request, search: str = ""):
    with SessionLocal() as db:
        query = select(Candidate)

        if search:
            query = query.where(
                Candidate.name.ilike(f"%{search}%")
                | Candidate.position.ilike(f"%{search}%")
            )

        candidates = db.scalars(
            query.order_by(Candidate.id)
        ).all()

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "candidates": candidates,
                "statuses": statuses,
                "search": search
            }
        )


@app.post("/candidates/add")
def add_candidate(
    name: str = Form(...),
    position: str = Form(...)
):
    name = name.strip()
    position = position.strip()

    if not name or not position:
        raise HTTPException(
            status_code=400,
            detail="Name and position cannot be empty"
        )

    with SessionLocal() as db:
        candidate = Candidate(
            name=name,
            position=position,
            status="Applied"
        )

        db.add(candidate)
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.post("/candidates/{candidate_id}/status")
def update_status(
    candidate_id: int,
    status: str = Form(...)
):
    if status not in statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    with SessionLocal() as db:
        candidate = db.get(Candidate, candidate_id)

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found"
            )

        candidate.status = status
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.get("/api/candidates")
def get_candidates():
    with SessionLocal() as db:
        candidates = db.scalars(
            select(Candidate).order_by(Candidate.id)
        ).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "position": c.position,
                "status": c.status
            }
            for c in candidates
        ]


@app.get("/health")
def health_check():
    return {"status": "healthy"}
