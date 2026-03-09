"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging(settings.debug)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
)

# Configure CORS for local frontend development.
if settings.cors_origins_list == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(OperationalError)
async def database_exception_handler(_: Request, __: OperationalError) -> JSONResponse:
    """Return a short database error message instead of full stack trace."""

    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection failed. Check MYSQL_* in .env and MySQL service status."},
    )


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Health-check endpoint."""

    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_v1_prefix)
