# root of the project, which inits the FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .api.endpoints.devices import router as devices_router
from .api.endpoints.login import router as login_router
from .api.endpoints.plants import router as plants_router
from .api.endpoints.plants import router_historical as plants_router_historical
from .api.endpoints.sensor_threshold import router as sensor_threshold_router
from .api.endpoints.tags import Tag
from .api.endpoints.users import router as users_router
from .core.settings import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
handler = Mangum(app)


@app.get("/healthcheck", tags=[Tag.HEALTHCHECK])
def healthcheck():
    return {"status": "ok"}


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://develop--smartpot.netlify.app",
        "https://smartpot.netlify.app",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(users_router)
app.include_router(plants_router)
app.include_router(devices_router)
app.include_router(plants_router_historical)
app.include_router(sensor_threshold_router)
