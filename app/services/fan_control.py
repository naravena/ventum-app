import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Optional
from ..models.config import FanConfig, ControlCurve, AlertConfig


class FanControlService:
    def __init__(self, history_service):
        self.history = history_service
        self.config_file = Path("/etc/fancontrol.json")
        self.config = self._load_default_config()
        self.current_pwm = {"fan1": 90, "fan2": 14}
        self.lock = asyncio.Lock()

    def _load_default_config(self) -> FanConfig:
        """Carga la configuración por defecto o desde archivo"""
        default_config = FanConfig(
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

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return FanConfig(**json.load(f))
            except Exception as e:
                print(f"Error loading config: {e}")

        return default_config

    async def initialize(self):
        """Inicialización del controlador"""
        await self._apply_pwm("fan1", self.current_pwm["fan1"])
        await self._apply_pwm("fan2", self.current_pwm["fan2"])
        asyncio.create_task(self._monitor_loop())

    async def cleanup(self):
        """Limpieza al detener el servicio"""
        pass

    async def _monitor_loop(self):
        """Bucle principal de monitorización"""
        while True:
            try:
                await self._update_sensors()
                await self._check_alerts()
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(5)

    async def _update_sensors(self):
        """Actualiza los valores de los sensores"""
        temp = await self._read_sensor("temp2")
        fan1_rpm = await self._read_sensor("fan1")
        fan2_rpm = await self._read_sensor("fan2")

        # Control automático de fan1 basado en temperatura
        new_pwm = self._calculate_pwm(temp)
        await self._apply_pwm("fan1", new_pwm)

        # Mantener fan2 constante
        await self._apply_pwm("fan2", self.current_pwm["fan2"])

        # Guardar histórico
        self.history.add_record({
            "timestamp": int(time.time()),
            "temp": temp,
            "fan1_rpm": fan1_rpm,
            "fan2_rpm": fan2_rpm,
            "pwm1": self.current_pwm["fan1"],
            "pwm2": self.current_pwm["fan2"]
        })

    def _calculate_pwm(self, temp: float) -> int:
        """Calcula el valor PWM basado en la curva de control"""
        curve = self.config.fan1.curve
        current_pwm = self.current_pwm["fan1"]

        # Ordenar puntos de la curva por temperatura
        curve_sorted = sorted(curve, key=lambda x: x[0])

        # Encontrar el segmento adecuado
        for i in range(len(curve_sorted) - 1):
            t1, pwm1 = curve_sorted[i]
            t2, pwm2 = curve_sorted[i + 1]

            if t1 <= temp <= t2:
                # Interpolación lineal
                ratio = (temp - t1) / (t2 - t1)
                new_pwm = pwm1 + (pwm2 - pwm1) * ratio
                return min(max(int(new_pwm), self.config.fan1.min_pwm), self.config.fan1.max_pwm)

        # Fuera de rango - usar extremos
        if temp < curve_sorted[0][0]:
            return curve_sorted[0][1]
        return curve_sorted[-1][1]

    async def _apply_pwm(self, fan: str, value: int):
        """Aplica un valor PWM al ventilador con seguridad"""
        async with self.lock:
            # Aplicar límites de hardware
            if fan == "fan1":
                value = max(self.config.fan1.min_pwm, min(value, 255))
            elif fan == "fan2":
                value = max(self.config.fan2.min_pwm, min(value, 255))

            # Aplicar histeresis para evitar oscilaciones
            current = self.current_pwm[fan]
            if abs(value - current) < 5:  # Pequeño umbral de cambio
                return

            # Escribir al hardware (necesita sudo)
            pwm_file = f"/sys/class/hwmon/hwmon0/pwm{1 if fan == 'fan1' else 2}"
            try:
                with open(pwm_file, 'w') as f:
                    f.write(str(value))
                self.current_pwm[fan] = value
            except Exception as e:
                print(f"Error writing PWM {fan}: {e}")

    async def _read_sensor(self, sensor: str) -> float:
        """Lee un valor del sensor del hardware"""
        try:
            if sensor.startswith("temp"):
                path = f"/sys/class/hwmon/hwmon0/{sensor}_input"
            else:  # fan
                path = f"/sys/class/hwmon/hwmon0/{sensor}_input"

            with open(path, 'r') as f:
                value = float(f.read().strip())

            # Convertir temperatura a °C (si es necesario)
            if sensor.startswith("temp"):
                return value / 1000
            return value
        except Exception as e:
            print(f"Error reading {sensor}: {e}")
            return 0.0

    async def _check_alerts(self):
        """Verifica condiciones de alerta"""
        last_record = self.history.get_last_record()
        if not last_record:
            return

        # Alerta de temperatura crítica (watchdog)
        if last_record["temp"] >= self.config.alerts.temp_critical:
            await self._apply_pwm("fan1", 255)
            await self._apply_pwm("fan2", 255)
            # TODO: Disparar alerta urgente

        # Alerta de temperatura alta
        elif last_record["temp"] >= self.config.alerts.temp_threshold:
            pass  # TODO: Disparar alerta

        # Alerta de RPM bajas
        if last_record["fan1_rpm"] <= self.config.alerts.rpm_threshold:
            pass  # TODO: Verificar duración y disparar alerta