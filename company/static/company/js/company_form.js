class CompanyManager {
    constructor() {
        this.baseUrl = '/company/company/';
        this.currentEditId = null;
        this.init();
        this.setupAxios();
    }

    setupAxios() {
        // Configuración de axios
        axios.defaults.timeout = 10000;
        axios.defaults.headers.common['X-CSRFToken'] = this.getCsrfToken();

        // Interceptor para manejo de errores
        axios.interceptors.response.use(
            response => response,
            error => {
                if (error.response) {
                    console.error('Error de respuesta:', error.response.status, error.response.data);
                    return Promise.reject(new Error(error.response.data.error || `HTTP ${error.response.status}: ${error.response.statusText}`));
                } else if (error.request) {
                    console.error('Error de red:', error.request);
                    return Promise.reject(new Error('Error de conexión. Verifica tu conexión a internet.'));
                } else {
                    console.error('Error de configuración:', error.message);
                    return Promise.reject(error);
                }
            }
        );
    }

    init() {
        this.bindEvents();
        this.loadCompanies();
        this.setupFileUpload();
    }

    bindEvents() {
        // Form submission
        document.getElementById('company-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });

        // Reset form
        document.getElementById('reset-form').addEventListener('click', () => {
            this.resetForm();
        });

        // Refresh list
        document.getElementById('refresh-list').addEventListener('click', () => {
            this.loadCompanies();
        });

        // Modal events
        const modal = document.getElementById('image-modal');
        const closeModal = document.querySelector('.close');
        
        closeModal.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    setupFileUpload() {
        const fileInput = document.getElementById('company-logo');
        const fileUpload = document.querySelector('.file-upload');
        const previewDiv = document.getElementById('file-preview');

        // Drag and drop
        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });

        fileUpload.addEventListener('dragleave', () => {
            fileUpload.classList.remove('dragover');
        });

        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                this.previewFile(files[0]);
            }
        });

        // File selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.previewFile(e.target.files[0]);
            } else {
                previewDiv.innerHTML = '';
            }
        });
    }

    previewFile(file) {
        const previewDiv = document.getElementById('file-preview');
        
        if (!file.type.startsWith('image/')) {
            this.showToast('Por favor selecciona un archivo de imagen', 'error');
            return;
        }

        if (file.size > 2 * 1024 * 1024) {
            this.showToast('El archivo es muy grande. Máximo 2MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewDiv.innerHTML = `
                <div class="preview-item">
                    <img src="${e.target.result}" alt="Preview">
                    <button type="button" class="preview-remove" onclick="companyManager.removePreview()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }

    removePreview() {
        document.getElementById('file-preview').innerHTML = '';
        document.getElementById('company-logo').value = '';
    }

    async submitForm() {
        const formData = new FormData();
        const companyName = document.getElementById('company-name').value.trim();
        const companyId = document.getElementById('company-id').value;
        const logoFile = document.getElementById('company-logo').files[0];

        if (!companyName) {
            this.showToast('El nombre de la empresa es requerido', 'error');
            return;
        }

        formData.append('company_name', companyName);
        if (companyId) {
            formData.append('id', companyId);
        }
        if (logoFile) {
            formData.append('logo', logoFile);
        }

        this.showLoading(true);
        
        try {
            const response = await axios.post(`${this.baseUrl}store/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            this.showToast(
                companyId ? 'Empresa actualizada correctamente' : 'Empresa creada correctamente',
                'success'
            );
            this.resetForm();
            this.loadCompanies();
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Error al guardar la empresa', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadCompanies() {
        this.showLoading(true);
        
        try {
            const response = await axios.get(this.baseUrl);
            const data = response.data;

            this.renderCompanies(data.data || data);
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al cargar las empresas', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    renderCompanies(companies) {
        const container = document.getElementById('companies-list');
        const noData = document.getElementById('no-companies');

        if (!companies || companies.length === 0) {
            container.innerHTML = '';
            noData.style.display = 'block';
            return;
        }

        noData.style.display = 'none';
        container.innerHTML = companies.map(company => this.createCompanyCard(company)).join('');
    }

    createCompanyCard(company) {
        const logoHtml = company.logo_url 
            ? `<img src="${company.logo_url}" alt="${company.company_name}" class="company-logo" onclick="companyManager.showImageModal('${company.logo_url}', '${company.company_name}')">`
            : `<div class="default-logo"><i class="fas fa-building"></i></div>`;

        const createdDate = company.created_at 
            ? new Date(company.created_at).toLocaleDateString('es-ES')
            : 'No disponible';

        return `
            <div class="company-card">
                <div class="company-header">
                    <div class="company-info">
                        <h3>${company.company_name}</h3>
                        <p><i class="fas fa-calendar"></i> Creada: ${createdDate}</p>
                        <p><i class="fas fa-image"></i> Logo: ${company.has_logo ? 'Sí' : 'No'}</p>
                    </div>
                    ${logoHtml}
                </div>
                
                <div class="company-actions">
                    <button class="btn-secondary btn-small" onclick="companyManager.editCompany(${company.id})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    
                    ${company.has_logo ? `
                        <button class="btn-secondary btn-small" onclick="companyManager.deleteLogo(${company.id})">
                            <i class="fas fa-trash"></i> Logo
                        </button>
                    ` : ''}
                    
                    <button class="btn-danger btn-small" onclick="companyManager.deleteCompany(${company.id})">
                        <i class="fas fa-trash-alt"></i> Empresa
                    </button>
                </div>
            </div>
        `;
    }

    async editCompany(id) {
        try {
            const response = await axios.get(`${this.baseUrl}${id}/show/`);
            const result = response.data;

            const company = result.data;
            document.getElementById('company-id').value = company.id;
            document.getElementById('company-name').value = company.company_name;
            document.getElementById('form-title').textContent = 'Editar Empresa';
            document.getElementById('submit-btn').innerHTML = '<i class="fas fa-save"></i> Actualizar Empresa';
            document.getElementById('reset-form').style.display = 'inline-flex';

            // Scroll to form
            document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });

            this.currentEditId = id;
            this.showToast('Empresa cargada para edición', 'info');
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al cargar la empresa', 'error');
        }
    }

    async deleteLogo(id) {
        if (!confirm('¿Estás seguro de eliminar el logo de esta empresa?')) {
            return;
        }

        try {
            await axios.delete(`${this.baseUrl}${id}/delete_logo/`, {
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            this.showToast('Logo eliminado correctamente', 'success');
            this.loadCompanies();
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Error al eliminar el logo', 'error');
        }
    }

    async deleteCompany(id) {
        if (!confirm('¿Estás seguro de eliminar esta empresa? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            await axios.delete(`${this.baseUrl}${id}/`, {
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            this.showToast('Empresa eliminada correctamente', 'success');
            this.loadCompanies();
            
            // Reset form if we were editing this company
            if (this.currentEditId === id) {
                this.resetForm();
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al eliminar la empresa', 'error');
        }
    }

    showImageModal(imageUrl, companyName) {
        const modal = document.getElementById('image-modal');
        const modalImage = document.getElementById('modal-image');
        const modalCaption = document.getElementById('modal-company-name');

        modalImage.src = imageUrl;
        modalCaption.textContent = companyName;
        modal.style.display = 'block';
    }

    resetForm() {
        document.getElementById('company-form').reset();
        document.getElementById('company-id').value = '';
        document.getElementById('form-title').textContent = 'Nueva Empresa';
        document.getElementById('submit-btn').innerHTML = '<i class="fas fa-save"></i> Guardar Empresa';
        document.getElementById('reset-form').style.display = 'none';
        document.getElementById('file-preview').innerHTML = '';
        this.currentEditId = null;
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        loading.style.display = show ? 'block' : 'none';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="${icons[type] || icons.info}"></i>
            ${message}
        `;

        container.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    getCsrfToken() {
        // Get CSRF token from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: get from meta tag if exists
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            return meta.getAttribute('content');
        }
        
        return '';
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.companyManager = new CompanyManager();
});

// Global functions for onclick events
window.companyManager = null;
