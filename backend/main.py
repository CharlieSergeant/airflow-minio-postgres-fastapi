import json
import logging
import os

from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.encoders import jsonable_encoder

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from backend import crud
from backend.api.api import public_api_router, private_api_router
from backend.core.config import settings

logging.basicConfig(level="INFO")

app = FastAPI(
    title=settings.PROJECT_NAME,docs_url="/api/docs", openapi_url="/api",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(public_api_router)
app.include_router(private_api_router)