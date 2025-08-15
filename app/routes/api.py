from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ..models.sensor import SensorData
from ..services.fan_control import FanControlService
from ..models.config import FanConfig

router = APIRouter()
security = HTTPBasic()

@router.get("/sensors", response_model=SensorData)
async def get_sensors(fan_control: FanControlService = Depends()):
    """Obtiene los valores actuales de los sensores"""
    last_record = fan_control.history.get_last_record()
    if not last_record:
        raise HTTPException(status_code=503, detail="No hay datos disponibles")
    return last_record

@router.post("/control/pwm")
async def set_pwm(fan1: int = None, fan2: int = None,
                 fan_control: FanControlService = Depends(),
                 credentials: HTTPBasicCredentials = Depends(security)):
    """Establece valores PWM manualmente"""
    # Aquí iría la lógica de autenticación
    if fan1 is not None:
        await fan_control._apply_pwm("fan1", fan1)
    if fan2 is not None:
        await fan_control._apply_pwm("fan2", fan2)
    return {"status": "ok"}

@router.get("/diag")
async def system_diagnostics(fan_control: FanControlService = Depends()):
    """Diagnóstico del sistema"""
    return {
        "sensors_accessible": await fan_control.check_sensors_access(),
        "pwm_accessible": await fan_control.check_pwm_access(),
        "current_config": fan_control.config.dict()
    }