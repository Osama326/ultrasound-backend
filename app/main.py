from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.routes import auth, doctors, reports

settings.ensure_directories()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    settings.ensure_directories()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(doctors.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.mount("/static/uploads", StaticFiles(directory=settings.upload_path), name="uploads")
app.mount("/static/reports", StaticFiles(directory=settings.report_path), name="reports")


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}
