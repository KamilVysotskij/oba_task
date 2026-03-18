from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import EntityNotFoundError


async def entity_not_found_handler(
    request: Request,
    exc: EntityNotFoundError,
) -> JSONResponse:
    return JSONResponse(status_code=404, content={'detail': str(exc)})
