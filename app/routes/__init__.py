# Importar rutas para que estén disponibles
from .api import router as api_router
from .auth import router as auth_router
from .ws import router as ws_router

__all__ = ["api_router", "auth_router", "ws_router"]