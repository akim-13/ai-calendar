from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from core.entities import ORMBase
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from features.plannables.endpoints import events, tasks
from features.users import endpoints
from infra.db.session import _engine, _SessionLocal
from root.startup import startup
from shared.logger import configure_logging, get_logger

# TODO:
# - Point docker to correct entrypoint (here).
# - Get rid of `backend.` prefix in imports.
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
    ORMBase.metadata.create_all(bind=_engine)

    with _SessionLocal() as db:
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
        (endpoints.router, "/users", ["Users"]),
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
