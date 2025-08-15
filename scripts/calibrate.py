#!/usr/bin/env python3
import os
import time
import json
from pathlib import Path


def main():
    print("=== Script de Calibración de Ventiladores ===")
    print("Este script ayudará a determinar los valores mínimos de PWM para tus ventiladores.")

    # Verificar acceso root
    if os.geteuid() != 0:
        print("Error: Este script debe ejecutarse como root (sudo).")
        exit(1)

    # Configuración inicial
    config = {
        "fan1": {
            "min_pwm": None,
            "default_pwm": 90,
            "max_pwm": 255
        },
        "fan2": {
            "min_pwm": None,
            "default_pwm": 14,
            "max_pwm": 100
        }
    }

    # Calibrar fan1
    print("\n=== Calibrando Ventilador 1 (pwm1) ===")
    input("Desconecta temporalmente otros ventiladores si es necesario. Presiona Enter para continuar...")

    config["fan1"]["min_pwm"] = calibrate_fan("fan1", "pwm1")

    # Calibrar fan2
    print("\n=== Calibrando Ventilador 2 (pwm2) ===")
    config["fan2"]["min_pwm"] = calibrate_fan("fan2", "pwm2")

    # Guardar configuración
    config_path = Path("/etc/fancontrol.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\nConfiguración guardada en {config_path}")
    print("Calibración completada. Puedes iniciar el servicio fancontrol.")


def calibrate_fan(fan_name: str, pwm_name: str) -> int:
    """Encuentra el valor PWM mínimo para que el ventilador arranque"""
    print(f"\nDeterminando PWM mínimo para {fan_name} ({pwm_name})...")

    # Detener ventilador
    set_pwm(pwm_name, 0)
    time.sleep(2)

    # Buscar punto de arranque
    min_pwm = None
    for pwm in range(0, 255, 2):
        set_pwm(pwm_name, pwm)
        time.sleep(1)

        rpm = get_rpm(fan_name)
        print(f"PWM={pwm:3d} → RPM={rpm:5.0f}")

        if rpm > 100:  # Umbral de arranque
            min_pwm = pwm
            print(f"\n¡Ventilador {fan_name} arrancó a PWM={min_pwm}!")
            break

    if min_pwm is None:
        print(f"Error: No se pudo hacer arrancar {fan_name} incluso a PWM máximo.")
        exit(1)

    # Aplicar histeresis (bajar hasta que se detenga)
    print("\nDeterminando punto de parada...")
    for pwm in range(min_pwm, 0, -1):
        set_pwm(pwm_name, pwm)
        time.sleep(1)

        rpm = get_rpm(fan_name)
        print(f"PWM={pwm:3d} → RPM={rpm:5.0f}")

        if rpm < 100:
            stop_pwm = pwm + 1
            print(f"\nVentilador {fan_name} se detuvo a PWM={pwm}, usando PWM={stop_pwm} como mínimo seguro.")
            return stop_pwm

    return min_pwm


def set_pwm(pwm_name: str, value: int):
    """Establece el valor PWM"""
    path = f"/sys/class/hwmon/hwmon0/{pwm_name}"
    try:
        with open(path, 'w') as f:
            f.write(str(value))
    except Exception as e:
        print(f"Error escribiendo PWM: {e}")
        exit(1)


def get_rpm(fan_name: str) -> float:
    """Lee las RPM del ventilador"""
    path = f"/sys/class/hwmon/hwmon0/{fan_name}_input"
    try:
        with open(path, 'r') as f:
            return float(f.read().strip())
    except Exception as e:
        print(f"Error leyendo RPM: {e}")
        return 0.0


if __name__ == "__main__":
    main()