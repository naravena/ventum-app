# FanControl Proxmox - Monitorización y Control de Ventiladores

## Descripción

Aplicación web completa para monitorizar y controlar en tiempo real la temperatura del CPU y las RPM de los ventiladores en servidores Linux (Proxmox/Debian). Ofrece:

- Monitorización en tiempo real de sensores
- Control manual y automático de ventiladores
- Alertas configurables
- Histórico de datos y gráficas interactivas
- Modo oscuro/claro automático

## Características Principales

### Monitorización
- Temperatura del CPU en tiempo real (sensor temp2)
- RPM de los ventiladores (fan1, fan2)
- Valores PWM actuales (pwm1, pwm2)

### Control
- **Modo manual**: Ajuste directo de valores PWM
- **Control automático**: Curva personalizable basada en temperatura
- **Perfiles predefinidos**: Modo normal, silencioso, etc.
- **Histeresis**: Evita oscilaciones frecuentes

### Alertas
- Temperatura crítica (≥85°C)
- Fallo de ventiladores (RPM <500 por 5 segundos)
- Watchdog (PWM máximo si ≥95°C)
- Notificaciones configurables

### Seguridad
- Autenticación básica HTTP
- Rate-limiting para cambios
- Permisos específicos via sudoers

## Requisitos del Sistema

- Proxmox/Debian (otras distros pueden requerir ajustes)
- Python 3.7+
- Acceso root para configuración inicial
- Sensores de hardware accesibles en `/sys/class/hwmon/`

## Instalación

### Método 1: Instalación directa

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/fancontrol-proxmox.git
   cd fancontrol-proxmox
   ```

2. Instalar dependencias:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   pip3 install -r requirements.txt
   ```

3. Ejecutar script de calibración (como root):
   ```bash
   sudo scripts/calibrate.py
   ```

4. Iniciar el servicio:
   ```bash
   sudo scripts/setup_systemd.sh
   ```

### Método 2: Usando Docker

1. Construir la imagen:
   ```bash
   docker-compose build
   ```

2. Iniciar el contenedor:
   ```bash
   docker-compose up -d
   ```

## Uso

### Acceso a la interfaz web
Abre tu navegador en:
```
http://tu-servidor:8000
```

### Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interfaz web principal |
| `/sensors` | GET | Datos actuales de sensores (JSON) |
| `/stream` | GET | Streaming de datos (SSE) |
| `/control/pwm` | POST | Cambiar valores PWM manualmente |
| `/control/curve` | POST | Configurar curva automática |
| `/profiles/apply` | POST | Aplicar perfil predefinido |
| `/diag` | GET | Diagnóstico del sistema |

### Autenticación
Los endpoints de control requieren autenticación básica:
- Usuario: `admin`
- Contraseña: `fancontrol` (cambiar en producción)

## Configuración

El archivo principal de configuración está en:
```
/etc/fancontrol.json
```

Ejemplo de configuración:
```json
{
  "fan1": {
    "min_pwm": 22,
    "max_pwm": 255,
    "curve": [[50, 90], [80, 255]],
    "hysteresis": 3
  },
  "fan2": {
    "min_pwm": 4,
    "max_pwm": 100,
    "curve": [[0, 14]],
    "hysteresis": 0
  },
  "alerts": {
    "temp_threshold": 85,
    "rpm_threshold": 500,
    "temp_critical": 95
  }
}
```

## Comandos útiles

- Ver estado del servicio:
  ```bash
  sudo systemctl status fancontrol
  ```

- Ver logs:
  ```bash
  journalctl -u fancontrol -f
  ```

- Reiniciar servicio:
  ```bash
  sudo systemctl restart fancontrol
  ```

## Solución de problemas

1. **Error de permisos**:
   ```bash
   sudo chmod -R 777 /sys/class/hwmon/hwmon0/
   ```

2. **Sensores no detectados**:
   Verifica la ruta correcta de tus sensores con:
   ```bash
   ls -l /sys/class/hwmon/
   ```

3. **Problemas con Docker**:
   Asegúrate de tener los dispositivos mapeados correctamente en el docker-compose.yml

## Contribución

Contribuciones son bienvenidas. Por favor abre un issue o pull request en GitHub.

## Licencia

MIT License