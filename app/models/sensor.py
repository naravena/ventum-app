from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    """Modelo para datos de sensores"""
    timestamp: int
    temp: float
    fan1_rpm: float
    fan2_rpm: float
    pwm1: int
    pwm2: int

    @property
    def datetime(self) -> datetime:
        """Convierte timestamp a datetime"""
        return datetime.fromtimestamp(self.timestamp)