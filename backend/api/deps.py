from pathlib import Path
from typing import Generator, Optional
from pydantic import BaseModel
from backend.db.session import SessionLocal
from backend.core.config import Settings,get_settings

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException, Depends
from starlette.status import HTTP_403_FORBIDDEN

BASE_PATH = Path(__file__).resolve().parent.parent

class TokenData(BaseModel):
    username: Optional[str] = None

def get_db() -> Generator:
    try:
        db = SessionLocal()
        db.current_user_id = None
        yield db
    finally:
        db.close()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(settings: Settings = Depends(get_settings), api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )

