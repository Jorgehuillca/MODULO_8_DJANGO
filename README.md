# Módulo 8 con DJANGO 

# Meta
Lograr arquitectura MVT y migrar correctamente el módulo 8 a un entorno Django.
---

##  Estructura del Proyecto  
```
modulo8/
├── company/                  # Datos empresariales
│   ├── models.py            # Modelos (Company, Logo)
│   ├── serializers.py       # Serializadores para APIs
│   ├── services.py          # Lógica de negocio
│   └── urls.py              # Endpoints: /api/company/
│
├── reports/                 # Sistema de reportes
│   ├── models.py            # Modelos (Report, Statistics)
│   ├── templates/           # Plantillas para PDF/HTML
│   └── services/            # Generación de reportes
│
├── emails/                  # Comunicaciones
│   ├── models.py            # Modelos (Email, Template)
│   ├── templates/           # Plantillas de correo
│   └── test_gmail.js        # Integración con Node.js
│
├── app_statistics/          # Dashboard y métricas
│   ├── models.py            # Modelos (Metric, Dashboard)
│   └── serializers.py       # APIs para gráficos
│
├── modulo8/                 # Configuración principal
│   ├── settings.py          # Config SMTP, APIs, etc.
│   └── urls.py             # Rutas globales
│
├── media/                   # Archivos subidos
│   └── company/logos/       # Logos empresariales
│
└── scripts_node/            # Integración con Node.js
    ├── package.json         # Dependencias (Nodemailer, etc.)
    └── test_gmail.js        # Pruebas de envío
```

# Funcionalidades Principales
1. Gestión Empresarial
Modelo Company en company/models.py:

class Company(models.Model):
    name = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='company/logos/')
    # ... (otros campos según tu models.py)

    - APIs REST en company/urls.py (DRF).

2. Reportes Automatizados
- Generación de reportes en reports/services/ (PDF/HTML).

- Plantillas personalizables en reports/templates/.

3. Sistema de Emails
- Integración con Node.js (Nodemailer) en emails/test_gmail.js.

- Plantillas de correo en emails/templates/.

4. Dashboard de Estadísticas
- APIs para gráficos en app_statistics/serializers.py.

- Datos históricos en app_statistics/models.py.

## Instalación
Requisitos:
- Python 3.10+, Node.js 18+

## Pasos
Clonar repositorio:

- git clone https://github.com/Jorgehuillca/MODULO_8_DJANGO.giturl
- cd MODULO_8_DJANGO

## Entorno virtual (Python):

- python -m venv .venv
- .\venv\Scripts\activate
- pip install -r requirements.txt

## Migraciones:

- python manage.py migrate
- python manage.py makemigrations
- python manage.py migrate

## Configurar Node.js (emails) y probar test de email:

- cd scripts_node
- node test_gmail.js

Endpoints API (Django REST Framework)

|Método	            | Ruta	                 |           Descripción                |
| ----------------- | ---------------------- | ------------------------------------ |
|GET	            | /api/company/	         |    Obtener datos empresariales       |
|POST	            | /api/reports/generate	 |        Generar reporte (PDF/HTML)    |
|GET	            | /api/statistics/	     |    Datos para gráficos del dashboard |

## Entregables

[ ] CRUD empresa funcional

[ ] Sistema de reportes operativo

[ ] Dashboard de estadísticas implementado

[ ] Sistema de email configurado

[ ] Notificaciones en tiempo real

[ ] Exportación de reportes a PDF/Excel

[ ] Tests unitarios y de integración
