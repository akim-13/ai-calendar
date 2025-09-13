from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.dbsetup import SessionLocal, engine
from backend.database.models import ORM_Base
from backend.misc.logger import configure_logging, get_logger
from backend.routers import achievements, calendars, events, tasks, users
from backend.services.startup import startup

# TODO:
# - Docstrings enforcement.
# - Logging
#   - Add more logging statements

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    log.warning("Starting up application.")

    ORM_Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        startup(db)

    # ↑ STARTUP CODE ↑
    yield  # App runs.
    # ↓ SHUTDOWN CODE ↓

    log.info("Shutting down application.")


app = FastAPI(lifespan=lifespan)

# Allow requests from the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],
)


def run_app() -> FastAPI:  # pragma: no cover
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
    app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
    app.include_router(events.router, prefix="/events", tags=["Events"])
    app.include_router(calendars.router, prefix="/calendars", tags=["Calendars"])

    return app
