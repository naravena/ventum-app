import time
from typing import List, Dict, Optional
from ..models.sensor import SensorData


class HistoryService:
    def __init__(self, max_records: int = 3600):
        """Servicio para mantener histórico de datos"""
        self.max_records = max_records  # 1 hora de datos a 1Hz
        self._data: List[SensorData] = []

    def add_record(self, record_data: Dict):
        """Añade un nuevo registro al histórico"""
        record = SensorData(**record_data)
        self._data.append(record)

        # Mantener sólo los últimos max_records
        if len(self._data) > self.max_records:
            self._data.pop(0)

    def get_last_record(self) -> Optional[SensorData]:
        """Obtiene el último registro"""
        return self._data[-1] if self._data else None

    def get_history(self, last_n: int = 60) -> List[SensorData]:
        """Obtiene los últimos N registros"""
        return self._data[-last_n:] if self._data else []

    def clear(self):
        """Limpia el histórico"""
        self._data = []