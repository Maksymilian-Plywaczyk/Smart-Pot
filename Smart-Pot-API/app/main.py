# root of the project, which inits the FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models.plant as plant_model
import app.models.user as user_model
from app.api.endpoints.login import router as login_router
from app.api.endpoints.plants import router as plants_router
from app.api.endpoints.users import router as users_router
from app.core.settings import settings
from app.db.session import engine

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

user_model.Base.metadata.create_all(bind=engine)
plant_model.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(users_router)
app.include_router(plants_router)
