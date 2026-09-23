from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

router = APIRouter(tags=["Health Module"])


@router.get(
    "/health", summary="Health Check", description="Check the health of the API"
)
def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "Ok is Healthy"}, status_code=200)
