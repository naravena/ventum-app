document.addEventListener('DOMContentLoaded', function() {
    // Configuración inicial
    let currentData = {
        temp: null,
        fan1_rpm: null,
        fan2_rpm: null,
        pwm1: null,
        pwm2: null
    };

    let historyData = [];
    let tempChart, rpmChart, curveChart;

    // Inicializar gráficas
    initCharts();

    // Manejar tema oscuro/claro
    setupThemeToggle();

    // Conectar a SSE para actualizaciones en tiempo real
    setupEventSource();

    // Configurar controles manuales
    setupManualControls();

    // Actualizar la UI con nuevos datos
    function updateUI(data) {
        // Actualizar valores numéricos
        document.getElementById('cpu-temp').textContent = `${data.temp}°C`;
        document.getElementById('fan1-rpm').textContent = data.fan1_rpm;
        document.getElementById('fan2-rpm').textContent = data.fan2_rpm;
        document.getElementById('fan1-pwm').textContent = data.pwm1;
        document.getElementById('fan2-pwm').textContent = data.pwm2;

        // Actualizar sliders
        document.getElementById('fan1-slider').value = data.pwm1;
        document.getElementById('fan2-slider').value = data.pwm2;
        document.getElementById('fan1-slider-value').textContent = data.pwm1;
        document.getElementById('fan2-slider-value').textContent = data.pwm2;

        // Actualizar estado de temperatura
        updateTempStatus(data.temp);

        // Actualizar última actualización
        const now = new Date();
        document.getElementById('last-update').textContent =
            `Última actualización: ${now.toLocaleTimeString()}`;
    }

    function updateTempStatus(temp) {
        const statusElement = document.getElementById('cpu-status');
        if (temp >= 85) {
            statusElement.textContent = 'Crítico';
            statusElement.className = 'text-sm px-2 py-1 rounded-full bg-danger text-white';
        } else if (temp >= 70) {
            statusElement.textContent = 'Alto';
            statusElement.className = 'text-sm px-2 py-1 rounded-full bg-warning text-white';
        } else {
            statusElement.textContent = 'Normal';
            statusElement.className = 'text-sm px-2 py-1 rounded-full bg-success text-white';
        }
    }

    function initCharts() {
        // Gráfica de temperatura
        const tempCtx = document.getElementById('temp-chart').getContext('2d');
        tempChart = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperatura CPU (°C)',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        suggestedMin: 30,
                        suggestedMax: 100
                    }
                }
            }
        });

        // Gráfica de RPM
        const rpmCtx = document.getElementById('rpm-chart').getContext('2d');
        rpmChart = new Chart(rpmCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Ventilador 1 (RPM)',
                        data: [],
                        borderColor: 'rgb(16, 185, 129)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: true
                    },
                    {
                        label: 'Ventilador 2 (RPM)',
                        data: [],
                        borderColor: 'rgb(168, 85, 247)',
                        backgroundColor: 'rgba(168, 85, 247, 0.1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }

    function updateCharts(data) {
        // Limitar histórico a 60 puntos (1 minuto a 1Hz)
        if (tempChart.data.labels.length > 60) {
            tempChart.data.labels.shift();
            tempChart.data.datasets[0].data.shift();

            rpmChart.data.labels.shift();
            rpmChart.data.datasets[0].data.shift();
            rpmChart.data.datasets[1].data.shift();
        }

        // Añadir nuevos datos
        const now = new Date();
        const timeStr = `${now.getMinutes()}:${now.getSeconds()}`;

        tempChart.data.labels.push(timeStr);
        tempChart.data.datasets[0].data.push(data.temp);
        tempChart.update();

        rpmChart.data.labels.push(timeStr);
        rpmChart.data.datasets[0].data.push(data.fan1_rpm);
        rpmChart.data.datasets[1].data.push(data.fan2_rpm);
        rpmChart.update();
    }

    function setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        const themeIcon = document.getElementById('theme-icon');

        // Comprobar preferencias del sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.documentElement.classList.add('dark');
            themeIcon.setAttribute('d', 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z');
        } else {
            document.documentElement.classList.remove('dark');
            themeIcon.setAttribute('d', 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z');
        }

        // Manejar clic en el botón
        themeToggle.addEventListener('click', () => {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                themeIcon.setAttribute('d', 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z');
            } else {
                document.documentElement.classList.add('dark');
                themeIcon.setAttribute('d', 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z');
            }
        });
    }

    function setupEventSource() {
        const eventSource = new EventSource('/stream');

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            currentData = data;
            updateUI(data);
            updateCharts(data);
        };

        eventSource.onerror = () => {
            console.error('Error en la conexión SSE');
            eventSource.close();
            // Intentar reconectar después de 5 segundos
            setTimeout(setupEventSource, 5000);
        };
    }

    function setupManualControls() {
        const fan1Slider = document.getElementById('fan1-slider');
        const fan2Slider = document.getElementById('fan2-slider');
        const applyBtn = document.getElementById('apply-manual');

        // Actualizar valores al mover los sliders
        fan1Slider.addEventListener('input', () => {
            document.getElementById('fan1-slider-value').textContent = fan1Slider.value;
        });

        fan2Slider.addEventListener('input', () => {
            document.getElementById('fan2-slider-value').textContent = fan2Slider.value;
        });

        // Aplicar configuración manual
        applyBtn.addEventListener('click', async () => {
            const fan1Value = parseInt(fan1Slider.value);
            const fan2Value = parseInt(fan2Slider.value);

            try {
                const response = await fetch('/control/pwm', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        fan1: fan1Value,
                        fan2: fan2Value
                    })
                });

                if (!response.ok) {
                    throw new Error('Error al aplicar configuración');
                }

                // Actualizar UI con los nuevos valores
                currentData.pwm1 = fan1Value;
                currentData.pwm2 = fan2Value;
                updateUI(currentData);

                alert('Configuración aplicada correctamente');
            } catch (error) {
                console.error('Error:', error);
                alert('Error al aplicar configuración');
            }
        });
    }
});