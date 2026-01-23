from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

