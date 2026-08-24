from collections.abc import AsyncIterator # Imports a type used to describe the lifespan function. It tells Python and VS Code that the function pauses asynchronously at yield.
from contextlib import asynccontextmanager

from fastapi import FastAPI

@asynccontextmanager # this decorator means: Treat the code before yield as setup and the code after yield as cleanup.
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield

app = FastAPI(
    title="LeapScope API",
    lifespan=lifespan
)