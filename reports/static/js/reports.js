/**
 * Dashboard de Reportes - Sistema de Gestión de Citas
 * Script principal para manejar la interfaz y las llamadas a las APIs
 */

// Variables globales
//const API_BASE_URL = '';
const DATE_FORMAT = 'YYYY-MM-DD';

/**
 * Inicialización del dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Inicializa el dashboard con los valores por defecto
 */
function initializeDashboard() {
    // Establecer fecha actual por defecto
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('single-date').value = today;
    document.getElementById('start-date').value = today;
    document.getElementById('end-date').value = today;
    
    // Cargar reportes del día actual
    loadSingleDateReports();
    addExportButtons();
    
    console.log('Dashboard de Reportes iniciado correctamente');
}

/**
 * Función genérica para realizar peticiones a las APIs
 * @param {string} url - URL de la API
 * @returns {Promise} - Promise con los datos de respuesta
 */
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        showNotification('Error al cargar datos: ' + error.message, 'error');
        console.error('Error en fetchData:', error);
        throw error;
    }
}

/**
 * Muestra notificaciones toast en la interfaz
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (info, success, error)
 */
function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Determinar icono según el tipo
    const iconClass = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'info': 'info-circle'
    };
    
    notification.innerHTML = `
        <i class="fas fa-${iconClass[type] || 'info-circle'}"></i>
        ${message}
        <button onclick="this.parentElement.remove()" aria-label="Cerrar notificación">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    notifications.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Carga el reporte de citas por terapeuta
 * @param {string} date - Fecha en formato YYYY-MM-DD
 */
async function loadTherapistAppointments(date) {
    const loading = document.getElementById('loading-therapist-appointments');
    const tbody = document.getElementById('therapist-appointments-body');
    const totalEl = document.getElementById('total-appointments');
    
    loading.style.display = 'block';
    
    try {
        const data = await fetchData(`${window.API_URLS.appointmentsPerTherapist}?date=${date}`);
        
        tbody.innerHTML = '';
        totalEl.textContent = data.total_appointments_count || 0;
        
        if (data.therapists_appointments && data.therapists_appointments.length > 0) {
            data.therapists_appointments.forEach(therapist => {
                const percentage = data.total_appointments_count > 0 ? 
                    ((therapist.appointments_count / data.total_appointments_count) * 100).toFixed(1) : 0;
                
                const row = document.createElement('tr');
                const therapistName = [
                    therapist.paternal_lastname,
                    therapist.maternal_lastname, 
                    therapist.name
                ].filter(Boolean).join(' ');
                
                row.innerHTML = `
                    <td title="${therapistName}">${therapistName}</td>
                    <td><span class="badge">${therapist.appointments_count}</span></td>
                    <td><span class="percentage">${percentage}%</span></td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr class="no-data"><td colspan="3">No hay datos para esta fecha</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr class="no-data"><td colspan="3">Error al cargar los datos</td></tr>';
        totalEl.textContent = '0';
        console.error('Error loading therapist appointments:', error);
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Carga el reporte de pacientes por terapeuta
 * @param {string} date - Fecha en formato YYYY-MM-DD
 */
async function loadPatientsByTherapist(date) {
    const loading = document.getElementById('loading-patients');
    const container = document.getElementById('patients-container');
    
    loading.style.display = 'block';
    
    try {
        const data = await fetchData(`${window.API_URLS.patientsByTherapist}?date=${date}`);
        
        container.innerHTML = '';
        
        if (data && data.length > 0) {
            data.forEach(therapist => {
                const therapistDiv = document.createElement('div');
                therapistDiv.className = 'therapist-group';
                
                // Crear lista de pacientes
                const patientsHtml = therapist.patients.map(patient => 
                    `<div class="patient-item">
                        <span class="patient-name" title="${patient.patient}">${patient.patient}</span>
                        <span class="patient-appointments">${patient.appointments} cita${patient.appointments > 1 ? 's' : ''}</span>
                    </div>`
                ).join('');
                
                // Calcular total de citas para este terapeuta
                const totalAppointments = therapist.patients.reduce((sum, patient) => sum + patient.appointments, 0);
                
                therapistDiv.innerHTML = `
                    <h4 class="therapist-name">
                        <i class="fas fa-user-md"></i>
                        ${therapist.therapist}
                        <span class="patient-count">${therapist.patients.length} pacientes - ${totalAppointments} citas</span>
                    </h4>
                    <div class="patients-list">
                        ${patientsHtml}
                    </div>
                `;
                
                container.appendChild(therapistDiv);
            });
        } else {
            container.innerHTML = '<p class="no-data-message">No hay pacientes para esta fecha</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="no-data-message">Error al cargar los pacientes</p>';
        console.error('Error loading patients by therapist:', error);
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Carga el resumen de caja diaria
 * @param {string} date - Fecha en formato YYYY-MM-DD
 */
async function loadDailyCash(date) {
    const loading = document.getElementById('loading-cash');
    const container = document.getElementById('cash-summary');
    
    loading.style.display = 'block';
    
    try {
        const data = await fetchData(`${window.API_URLS.dailyCash}?date=${date}`);
        
        container.innerHTML = '';
        
        if (data && data.length > 0) {
            let total = 0;
            
            // Crear elementos de cada tipo de pago
            const cashItems = data.map(item => {
                total += item.total_payment;
                return `
                    <div class="cash-item">
                        <span class="payment-type">${item.payment_type}</span>
                        <span class="payment-amount">S/. ${item.total_payment.toFixed(2)}</span>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = `
                <div class="cash-items">
                    ${cashItems}
                </div>
                <div class="cash-total">
                    <strong>Total del día: S/. ${total.toFixed(2)}</strong>
                </div>
            `;
        } else {
            container.innerHTML = '<p class="no-data-message">No hay movimientos de caja para esta fecha</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="no-data-message">Error al cargar el resumen de caja</p>';
        console.error('Error loading daily cash:', error);
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Carga las citas en un rango de fechas
 * @param {string} startDate - Fecha de inicio en formato YYYY-MM-DD
 * @param {string} endDate - Fecha de fin en formato YYYY-MM-DD
 */
async function loadDateRangeAppointments(startDate, endDate) {
    const loading = document.getElementById('loading-date-range');
    const tbody = document.getElementById('date-range-body');
    
    loading.style.display = 'block';
    
    try {
        const data = await fetchData(`${window.API_URLS.appointmentsBetweenDates}?start_date=${startDate}&end_date=${endDate}`);
        
        tbody.innerHTML = '';
        
        if (data && data.length > 0) {
            data.forEach(appointment => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatDate(appointment.appointment_date)}</td>
                    <td>${appointment.appointment_hour}</td>
                    <td title="${appointment.therapist}">${appointment.therapist}</td>
                    <td title="${appointment.patient}">${appointment.patient}</td>
                    <td class="payment-cell">S/. ${parseFloat(appointment.payment).toFixed(2)}</td>
                    <td><span class="payment-type-badge">${appointment.payment_type}</span></td>
                `;
                tbody.appendChild(row);
            });
            
            // Agregar fila con resumen
            const totalPayment = data.reduce((sum, app) => sum + parseFloat(app.payment), 0);
            const summaryRow = document.createElement('tr');
            summaryRow.className = 'summary-row';
            summaryRow.innerHTML = `
                <td colspan="4"><strong>Total (${data.length} citas)</strong></td>
                <td class="payment-cell"><strong>S/. ${totalPayment.toFixed(2)}</strong></td>
                <td></td>
            `;
            tbody.appendChild(summaryRow);
            
        } else {
            tbody.innerHTML = '<tr class="no-data"><td colspan="6">No hay citas en este rango de fechas</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr class="no-data"><td colspan="6">Error al cargar las citas</td></tr>';
        console.error('Error loading date range appointments:', error);
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Carga todos los reportes para una fecha específica
 */
function loadSingleDateReports() {
    const date = document.getElementById('single-date').value;
    
    if (!date) {
        showNotification('Por favor selecciona una fecha', 'error');
        return;
    }
    
    if (!isValidDate(date)) {
        showNotification('Formato de fecha inválido', 'error');
        return;
    }
    
    // Cargar todos los reportes de fecha única
    loadTherapistAppointments(date);
    loadPatientsByTherapist(date);
    loadDailyCash(date);
    
    showNotification(`Reportes cargados para el ${formatDate(date)}`, 'success');
}

/**
 * Carga el reporte de citas en rango de fechas
 */
function loadDateRangeReport() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (!startDate || !endDate) {
        showNotification('Por favor selecciona ambas fechas', 'error');
        return;
    }
    
    if (!isValidDate(startDate) || !isValidDate(endDate)) {
        showNotification('Formato de fecha inválido', 'error');
        return;
    }
    
    if (startDate > endDate) {
        showNotification('La fecha de inicio no puede ser mayor a la fecha fin', 'error');
        return;
    }
    
    loadDateRangeAppointments(startDate, endDate);
    showNotification(`Citas cargadas del ${formatDate(startDate)} al ${formatDate(endDate)}`, 'success');
}

/**
 * Utilidades
 */

/**
 * Valida si una fecha tiene el formato correcto
 * @param {string} dateString - Fecha en formato YYYY-MM-DD
 * @returns {boolean} - True si es válida
 */
function isValidDate(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;
    
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

/**
 * Formatea una fecha para mostrar en la interfaz
 * @param {string} dateString - Fecha en formato YYYY-MM-DD
 * @returns {string} - Fecha formateada
 */
function formatDate(dateString) {
    try {
        const date = new Date(dateString + 'T00:00:00');
        return date.toLocaleDateString('es-PE', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return dateString; // Fallback al formato original
    }
}

/**
 * Maneja errores de red y muestra mensajes apropiados
 * @param {Error} error - Error capturado
 * @param {string} context - Contexto donde ocurrió el error
 */
function handleNetworkError(error, context = '') {
    console.error(`Network error in ${context}:`, error);
    
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        showNotification('Error de conexión. Verifica tu conexión a internet.', 'error');
    } else if (error.message.includes('500')) {
        showNotification('Error interno del servidor. Contacta al administrador.', 'error');
    } else if (error.message.includes('404')) {
        showNotification('Recurso no encontrado. Verifica la configuración.', 'error');
    } else {
        showNotification(`Error inesperado: ${error.message}`, 'error');
    }
}

function addExportButtons() {
    // Reporte 1: Citas por Terapeuta
    const report1Card = document.querySelector('.report-card:nth-child(1) .card-header');
    const pdfButton1 = createExportButton('PDF', 'btn-pdf', () => {
        const date = document.getElementById('single-date').value;
        window.open(`${window.API_URLS.appointmentsPerTherapist.replace('appointments-per-therapist', 'pdf/citas-terapeuta')}?date=${date}`, '_blank');
    });
    report1Card.appendChild(pdfButton1);

    // Reporte 2: Pacientes por Terapeuta
    const report2Card = document.querySelector('.report-card:nth-child(2) .card-header');
    const pdfButton2 = createExportButton('PDF', 'btn-pdf', () => {
        const date = document.getElementById('single-date').value;
        window.open(`${window.API_URLS.patientsByTherapist.replace('patients-by-therapist', 'pdf/pacientes-terapeuta')}?date=${date}`, '_blank');
    });
    report2Card.appendChild(pdfButton2);

    // Reporte 3: Resumen de Caja
    const report3Card = document.querySelector('.report-card:nth-child(3) .card-header');
    const pdfButton3 = createExportButton('PDF', 'btn-pdf', () => {
        const date = document.getElementById('single-date').value;
        window.open(`${window.API_URLS.dailyCash.replace('daily-cash', 'pdf/resumen-caja')}?date=${date}`, '_blank');
    });
    report3Card.appendChild(pdfButton3);

    // Reporte 4: Citas en Rango (Excel)
    const report4Card = document.querySelector('.report-card:nth-child(4) .card-header');
    const excelButton = createExportButton('Excel', 'btn-excel', () => {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        window.open(`${window.API_URLS.appointmentsBetweenDates.replace('appointments-between-dates', 'excel/citas-rango')}?start_date=${startDate}&end_date=${endDate}`, '_blank');
    });
    report4Card.appendChild(excelButton);
}

function createExportButton(text, className, onClick) {
    const button = document.createElement('button');
    button.className = `btn ${className}`;
    button.innerHTML = `<i class="fas fa-file-${className.split('-')[1]}"></i> ${text}`;
    button.onclick = onClick;
    return button;
}

// Exportar funciones para uso global (si es necesario)
window.loadSingleDateReports = loadSingleDateReports;
window.loadDateRangeReport = loadDateRangeReport;