#!/bin/bash

# Crear usuario de servicio
if ! id "fancontrol" &>/dev/null; then
    useradd -r -s /bin/false fancontrol
fi

# Crear directorios
mkdir -p /opt/fancontrol
mkdir -p /var/log/fancontrol
chown fancontrol:fancontrol /var/log/fancontrol

# Copiar archivos
cp -r app /opt/fancontrol/
cp requirements.txt /opt/fancontrol/
chown -R fancontrol:fancontrol /opt/fancontrol

# Instalar dependencias
apt-get update
apt-get install -y python3-pip
pip3 install -r /opt/fancontrol/requirements.txt

# Configurar sudoers
echo "fancontrol ALL=(root) NOPASSWD: /bin/chmod 666 /sys/class/hwmon/hwmon0/pwm*" > /etc/sudoers.d/fancontrol
echo "fancontrol ALL=(root) NOPASSWD: /bin/chmod 444 /sys/class/hwmon/hwmon0/fan*_input" >> /etc/sudoers.d/fancontrol
echo "fancontrol ALL=(root) NOPASSWD: /bin/chmod 444 /sys/class/hwmon/hwmon0/temp*_input" >> /etc/sudoers.d/fancontrol
chmod 440 /etc/sudoers.d/fancontrol

# Crear servicio systemd
cat > /etc/systemd/system/fancontrol.service <<EOF
[Unit]
Description=FanControl Service for Proxmox/Debian
After=network.target

[Service]
User=fancontrol
WorkingDirectory=/opt/fancontrol
ExecStart=/usr/bin/python3 -m app.main
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
StandardOutput=file:/var/log/fancontrol/out.log
StandardError=file:/var/log/fancontrol/err.log

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar servicio
systemctl daemon-reload
systemctl enable fancontrol
systemctl start fancontrol

echo "Instalación completada. Servicio fancontrol iniciado."