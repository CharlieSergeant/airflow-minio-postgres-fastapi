import logging
from fastapi import APIRouter, Request, Depends

router = APIRouter()

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@router.get("/private_healthcheck")
def Private_Healthcheck():
    return "Alive. Secure Route"
