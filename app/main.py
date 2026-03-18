from fastapi import Depends, FastAPI

from app.api.errors import entity_not_found_handler
from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import EntityNotFoundError
from app.core.security import require_api_key

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version='1.0.0',
    description=(
        'REST API справочника организаций, зданий и видов деятельности. '
    ),
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_tags=[
        {
            'name': 'Organizations',
            'description': 'Поиск и получение карточек организаций.',
        },
        {'name': 'Buildings', 'description': 'Справочник зданий.'},
        {
            'name': 'Activities',
            'description': 'Справочник видов деятельности и их дерево.',
        },
    ],
)

app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get(
    '/health',
    tags=['Health'],
    dependencies=[Depends(require_api_key)],
)
async def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}
