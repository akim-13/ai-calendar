from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.db_session import SessionLocal, engine
from backend.database.models.base import ORMBase
from backend.misc.logger import configure_logging, get_logger
from backend.routers import events, tasks, users
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

    # TODO: Switch to using Alembic in the future.
    # ORMBase.metadata.drop_all(bind=engine)
    ORMBase.metadata.create_all(bind=engine)

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


def run_app() -> FastAPI:
    routers = [
        (users.router, "/users", ["Users"]),
        (tasks.router, "/tasks", ["Tasks"]),
        (events.router, "/events", ["Events"]),
    ]
    for router, prefix, tags in routers:
        app.include_router(
            router,
            prefix=prefix,
            tags=tags,  # type: ignore
        )

    return app
