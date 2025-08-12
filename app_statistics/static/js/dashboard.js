let charts = {};

// Configuración de la API
const API_BASE = '/statistics/statistics/metricas/';

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setThisMonth();
    loadStatistics();
});

/**
 * Establece la fecha de hoy en los controles
 */
function setToday() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').value = today;
    document.getElementById('endDate').value = today;
}

/**
 * Establece las fechas del mes actual
 */
function setThisMonth() {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];
    
    document.getElementById('startDate').value = start;
    document.getElementById('endDate').value = end;
}

/**
 * Carga las estadísticas desde la API
 */
async function loadStatistics() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!startDate || !endDate) {
        showError('Por favor selecciona ambas fechas');
        return;
    }

    if (new Date(startDate) > new Date(endDate)) {
        showError('La fecha de inicio no puede ser mayor que la fecha de fin');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE}?start=${startDate}&end=${endDate}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        renderDashboard(data);
        hideLoading();

    } catch (error) {
        console.error('Error:', error);
        showError(`Error al cargar estadísticas: ${error.message}`);
        hideLoading();
    }
}

/**
 * Renderiza todo el dashboard con los datos recibidos
 */
function renderDashboard(data) {
    // Métricas principales
    document.getElementById('totalPacientes').textContent = data.metricas.ttlpacientes || 0;
    document.getElementById('totalSesiones').textContent = data.metricas.ttlsesiones || 0;
    document.getElementById('totalGanancias').textContent = 
        `S/ ${(data.metricas.ttlganancias || 0).toFixed(2)}`;

    // Gráficos
    renderIngresosChart(data.ingresos);
    renderSesionesChart(data.sesiones);
    renderPagoChart(data.tipos_pago);
    renderPacientesChart(data.tipos_pacientes);

    // Terapeutas
    renderTherapists(data.terapeutas);

    // Mostrar dashboard
    document.getElementById('dashboard-content').style.display = 'block';
}

/**
 * Renderiza el gráfico de ingresos por día
 */
function renderIngresosChart(ingresos) {
    const ctx = document.getElementById('ingresosChart').getContext('2d');
    
    if (charts.ingresos) charts.ingresos.destroy();

    charts.ingresos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(ingresos),
            datasets: [{
                label: 'Ingresos (S/)',
                data: Object.values(ingresos),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'S/ ' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renderiza el gráfico de sesiones por día
 */
function renderSesionesChart(sesiones) {
    const ctx = document.getElementById('sesionesChart').getContext('2d');
    
    if (charts.sesiones) charts.sesiones.destroy();

    charts.sesiones = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(sesiones),
            datasets: [{
                label: 'Sesiones',
                data: Object.values(sesiones),
                backgroundColor: 'rgba(245, 87, 108, 0.2)',
                borderColor: 'rgba(245, 87, 108, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

/**
 * Renderiza el gráfico de tipos de pago
 */
function renderPagoChart(tipos_pago) {
    const ctx = document.getElementById('pagoChart').getContext('2d');
    
    if (charts.pago) charts.pago.destroy();

    if (Object.keys(tipos_pago).length === 0) {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No hay datos', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];

    charts.pago = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(tipos_pago),
            datasets: [{
                data: Object.values(tipos_pago),
                backgroundColor: colors.slice(0, Object.keys(tipos_pago).length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Renderiza el gráfico de tipos de pacientes
 */
function renderPacientesChart(tipos_pacientes) {
    const ctx = document.getElementById('pacientesChart').getContext('2d');
    
    if (charts.pacientes) charts.pacientes.destroy();

    charts.pacientes = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Tipo C', 'Tipo CC'],
            datasets: [{
                data: [tipos_pacientes.c, tipos_pacientes.cc],
                backgroundColor: ['#4CAF50', '#FF9800']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Renderiza la lista de terapeutas
 */
function renderTherapists(terapeutas) {
    const container = document.getElementById('therapistsList');
    
    if (!terapeutas || terapeutas.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No hay datos de terapeutas en el período seleccionado</p>';
        return;
    }

    container.innerHTML = terapeutas.map(terapeuta => `
        <div class="therapist-card">
            <div class="therapist-info">
                <div class="therapist-name">${terapeuta.terapeuta}</div>
                <div class="therapist-stats">
                    <span>📅 ${terapeuta.sesiones} sesiones</span>
                    <span>💰 S/ ${terapeuta.ingresos.toFixed(2)}</span>
                </div>
            </div>
            <div class="therapist-rating">⭐ ${terapeuta.raiting}/5</div>
        </div>
    `).join('');
}

/**
 * Muestra el indicador de carga
 */
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('dashboard-content').style.display = 'none';
}

/**
 * Oculta el indicador de carga
 */
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

/**
 * Oculta el mensaje de error
 */
function hideError() {
    document.getElementById('error').style.display = 'none';
}

/**
 * Formatea números grandes con separadores de miles
 */
function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}

/**
 * Formatea monedas en soles peruanos
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN'
    }).format(amount);
}