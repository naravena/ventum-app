from typing import Dict, Any, Optional
from datetime import datetime, time
from ..models.config import FanConfig


class ProfileService:
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {
            "default": {
                "description": "Perfil predeterminado",
                "config": FanConfig(
                    fan1=ControlCurve(
                        min_pwm=22,
                        max_pwm=255,
                        curve=[(50, 90), (80, 255)],
                        hysteresis=3
                    ),
                    fan2=ControlCurve(
                        min_pwm=4,
                        max_pwm=100,
                        curve=[(0, 14)],
                        hysteresis=0
                    ),
                    alerts=AlertConfig(
                        temp_threshold=85,
                        rpm_threshold=500,
                        temp_critical=95
                    )
                )
            },
            "silent": {
                "description": "Modo silencioso (menos enfriamiento)",
                "config": FanConfig(
                    fan1=ControlCurve(
                        min_pwm=22,
                        max_pwm=180,
                        curve=[(60, 70), (85, 180)],
                        hysteresis=5
                    ),
                    fan2=ControlCurve(
                        min_pwm=4,
                        max_pwm=80,
                        curve=[(0, 10)],
                        hysteresis=0
                    ),
                    alerts=AlertConfig(
                        temp_threshold=90,
                        rpm_threshold=400,
                        temp_critical=100
                    )
                )
            }
        }

    def get_available_profiles(self) -> Dict[str, str]:
        """Obtiene los perfiles disponibles"""
        return {name: data["description"] for name, data in self.profiles.items()}

    def get_profile_config(self, profile_name: str) -> Optional[FanConfig]:
        """Obtiene la configuración de un perfil"""
        profile = self.profiles.get(profile_name)
        return profile["config"] if profile else None

    def get_time_based_profile(self) -> str:
        """Obtiene el perfil basado en la hora actual"""
        now = datetime.now().time()

        # Modo silencioso entre 22:00 y 07:00
        if time(22, 0) <= now or now <= time(7, 0):
            return "silent"
        return "default"