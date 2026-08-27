from collections.abc import AsyncGenerator # Imports a type used to describe the lifespan function. It tells Python and VS Code that the function pauses asynchronously at yield.
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings

from app.api.routers import health

@asynccontextmanager # this decorator means: Treat the code before yield as setup and the code after yield as cleanup.
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    yield

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

app.include_router(health.router)