from fastapi import APIRouter, Depends

from backend.api.deps import get_api_key
from backend.api.endpoints import public
from backend.api.endpoints import private


public_api_router = APIRouter(prefix="/api", tags=["Public Endpoints"])
public_api_router.include_router(public.router)

private_api_router = APIRouter(prefix="/api", tags=["Private Endpoints"],dependencies=[Depends(get_api_key)])
private_api_router.include_router(private.router)



