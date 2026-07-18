from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from routers import auth, food, health, chatbot, scanner, planner, habits, social, insights, streak
from database import engine, Base
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all tables (works for both SQLite and PostgreSQL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables ready")
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="NutriMind AI API",
    description="Smart Food & Health Companion Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(food.router, prefix="/api/food", tags=["Food"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(scanner.router, prefix="/api/scanner", tags=["Scanner"])
app.include_router(planner.router, prefix="/api/planner", tags=["Planner"])
app.include_router(habits.router, prefix="/api/habits", tags=["Habits"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(streak.router, prefix="/api/streak", tags=["Streak"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "NutriMind AI"}
