from pydantic import BaseModel, conint, conlist, validator
from typing import List, Tuple

class ControlCurve(BaseModel):
    """Configuración de curva de control para un ventilador"""
    min_pwm: conint(ge=0, le=255)
    max_pwm: conint(ge=0, le=255)
    curve: conlist(item_type=Tuple[float, int], min_items=1)
    hysteresis: conint(ge=0, le=10) = 3

    @validator('curve')
    def validate_curve(cls, v):
        # Ordenar curva por temperatura
        return sorted(v, key=lambda x: x[0])

class AlertConfig(BaseModel):
    """Configuración de alertas"""
    temp_threshold: float = 85.0
    rpm_threshold: int = 500
    temp_critical: float = 95.0
    email_notifications: bool = False
    telegram_notifications: bool = False

class FanConfig(BaseModel):
    """Configuración completa del sistema"""
    fan1: ControlCurve
    fan2: ControlCurve
    alerts: AlertConfig