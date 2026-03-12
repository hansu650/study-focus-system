"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dicts import router as dict_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.focus_sessions import router as focus_sessions_router
from app.api.v1.leaderboards import router as leaderboards_router
from app.api.v1.learning import router as learning_router
from app.api.v1.points import router as points_router
from app.api.v1.redeem_orders import router as redeem_orders_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(dict_router)
api_router.include_router(feedback_router)
api_router.include_router(users_router)
api_router.include_router(focus_sessions_router)
api_router.include_router(points_router)
api_router.include_router(leaderboards_router)
api_router.include_router(learning_router)
api_router.include_router(redeem_orders_router)