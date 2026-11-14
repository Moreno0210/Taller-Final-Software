
from fastapi import FastAPI

from core.config import settings

from routers import checkout


app = FastAPI(
    title=settings.PROJECT_NAME
)


app.include_router(
    checkout.router,
    prefix=settings.API_V1_STR
)


@app.get("/health")
async def health_check():

    return {
        "status": "online"
    }
