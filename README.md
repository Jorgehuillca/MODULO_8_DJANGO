## Módulo 08 - Empresa, Reportes y Comunicación (Django)

## Responsabilidades

## Aplicaciones y componentes para:

 - Modelo CompanyData

 - Sistema de reportes y estadísticas

 - Gestión de logos

 - Sistema de email

 - APIs de reportes y notificaciones

## Meta:

 - Lograr arquitectura MTV (Model-Template-View) con APIs REST para ser consumidas por React.

## Estructura en Django:

modulo8/
├── company/
│   ├── models.py        # CompanyData
│   ├── views.py         # APIViews para CRUD de empresa
│   ├── serializers.py   # Serializadores de CompanyData
│   ├── services.py      # Lógica de negocio de empresa
│   ├── urls.py          # Rutas de API /company
│   └── tests.py
├── reports/
│   ├── models.py        # Report
│   ├── views.py         # API para reportes
│   ├── serializers.py
│   ├── services.py      # Generación de reportes
│   ├── utils.py         # Funciones de exportación (PDF/Excel)
│   ├── urls.py
│   └── tests.py
├── statistics/
│   ├── models.py        # Statistics
│   ├── views.py         # API de estadísticas
│   ├── serializers.py
│   ├── services.py      # Cálculo de estadísticas
│   ├── urls.py
│   └── tests.py
├── emails/
│   ├── models.py        # Email log/history
│   ├── views.py         # API para enviar/ver emails
│   ├── serializers.py
│   ├── services.py      # Envío de correos
│   ├── templates/emails/email_restore.html
│   ├── urls.py
│   └── tests.py
└── notifications/
    ├── models.py        # Notification
    ├── views.py         # API para notificaciones
    ├── serializers.py
    ├── services.py
    ├── urls.py
    └── tests.py


## Modelos (models.py):

| Campo             | Tipo       |
| ----------------- | ---------- |
| name              | CharField  |
| ruc               | CharField  |
| address           | CharField  |
| phone             | CharField  |
| email             | EmailField |
| website           | URLField   |
| logo              | ImageField |
| description       | TextField  |
| opening\_hours    | JSONField  |
| privacy\_policy   | TextField  |
| terms\_conditions | TextField  |

## Report:

 - Tipo de reporte (patients, appointments, therapists, revenue, etc.)

 - Parámetros de filtro

 - Archivo generado (PDF o Excel)

 - Fecha de creación

## Statistics:

 - Tipo de estadística (dashboard, patients, appointments, revenue, etc.)

 - Datos (JSON)

## Email:

 - Destinatario(s)

 - Asunto

 - Cuerpo

 - Estado de envío

 - Fecha de envío

## Notification:

 - Título

 - Mensaje

 - Tipo (email, push, sms, whatsapp)

 - Estado (read / unread)

 - Fecha

## Vistas / APIs (views.py + urls.py):

Se implementarán usando Django REST Framework

| Método | Endpoint                       | Descripción                   |
| ------ | ------------------------------ | ----------------------------- |
| GET    | `/api/company`                 | Obtener datos de empresa      |
| PUT    | `/api/company`                 | Actualizar datos de empresa   |
| POST   | `/api/company/logo`            | Subir logo                    |
| GET    | `/api/reports/patients`        | Reporte de pacientes          |
| GET    | `/api/reports/appointments`    | Reporte de citas              |
| GET    | `/api/reports/therapists`      | Reporte de terapeutas         |
| GET    | `/api/reports/revenue`         | Reporte de ingresos           |
| POST   | `/api/reports/generate`        | Generar reporte personalizado |
| GET    | `/api/reports/{id}/download`   | Descargar reporte             |
| GET    | `/api/statistics/dashboard`    | Estadísticas del dashboard    |
| GET    | `/api/statistics/patients`     | Estadísticas de pacientes     |
| GET    | `/api/statistics/appointments` | Estadísticas de citas         |
| GET    | `/api/statistics/revenue`      | Estadísticas de ingresos      |
| POST   | `/api/emails/send`             | Enviar email                  |
| GET    | `/api/emails/history`          | Historial de emails           |
| POST   | `/api/notifications/send`      | Enviar notificación           |
| GET    | `/api/notifications`           | Listar notificaciones         |
| PUT    | `/api/notifications/{id}/read` | Marcar como leída             |


## Servicios (services.py):

 - CompanyService → CRUD empresa + subida de logo.

 - ReportService → Generación y exportación de reportes PDF/Excel.

 - StatisticsService → Consultas y agregaciones para estadísticas.

 - EmailService → Envío de correos usando EmailMessage o send_mass_mail.

 - NotificationService → Envío y gestión de notificaciones push, email, SMS, WhatsApp.

## Dependencias:

 - Django REST Framework → APIs REST

 - django-filter → Filtrado en reportes

 - Pillow → Manejo de imágenes (logo)

 - xhtml2pdf o WeasyPrint → Exportación a PDF

 - pandas / openpyxl → Exportación a Excel

 - Celery + Redis → Envío de emails/notificaciones en segundo plano

 - Chart.js (en React) → Visualización de estadísticas

## Entregables

[ ]  CRUD empresa funcional

[ ]  Sistema de reportes operativo

[ ]  Dashboard de estadísticas implementado

[ ]  Sistema de email configurado

[ ]  Notificaciones en tiempo real

[ ]  Exportación de reportes a PDF/Excel

[ ]  APIs documentadas en Swagger/DRF

[ ]  Integración lista para React

[ ]  Tests unitarios y de integración
