import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import api, auth, ws
from .services.history import HistoryService
from .services.fan_control import FanControlService

# Configuración inicial
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FanControl Proxmox",
    description="Sistema de monitorización y control de ventiladores para servidores Proxmox/Debian",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicios
history_service = HistoryService()
fan_control = FanControlService(history_service)

# Rutas
app.include_router(api.router)
app.include_router(auth.router)
app.include_router(ws.router)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    logger.info("Iniciando servicio FanControl")
    await fan_control.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al detener el servicio"""
    logger.info("Deteniendo servicio FanControl")
    await fan_control.cleanup()