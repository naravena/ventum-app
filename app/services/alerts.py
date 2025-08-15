import logging
from typing import Optional
from datetime import datetime, timedelta
from ..models.sensor import SensorData
from ..models.config import AlertConfig


class AlertService:
    def __init__(self, config: AlertConfig):
        self.config = config
        self.last_alert_time: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)

    def check_temp_alert(self, temp: float) -> bool:
        """Verifica alerta de temperatura"""
        if temp >= self.config.temp_critical:
            self._send_alert(f"Temperatura CRÍTICA: {temp}°C")
            return True
        elif temp >= self.config.temp_threshold:
            self._send_alert(f"Temperatura ALTA: {temp}°C")
            return True
        return False

    def check_rpm_alert(self, rpm: float, fan_name: str) -> bool:
        """Verifica alerta de RPM bajas"""
        if rpm <= self.config.rpm_threshold:
            self._send_alert(f"RPM BAJAS en {fan_name}: {rpm} RPM")
            return True
        return False

    def _send_alert(self, message: str):
        """Envía una alerta (implementación básica)"""
        now = datetime.now()

        # Evitar spam de alertas
        if self.last_alert_time and (now - self.last_alert_time) < timedelta(minutes=5):
            return

        self.last_alert_time = now
        self.logger.warning(f"ALERTA: {message}")

        # Aquí se podría implementar notificación por email/Telegram
        if self.config.email_notifications:
            pass  # Implementar envío de email

        if self.config.telegram_notifications:
            pass  # Implementar envío a Telegram