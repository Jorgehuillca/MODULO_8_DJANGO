from datetime import datetime
from django.utils.timezone import localtime
from django.db.models import Count, Q, Sum
from base_models.models import Appointment, PaymentType, Therapist  # Debes tener estos modelos creados
from django.db import models

class ReportService:
    def get_appointments_count_by_therapist(self, request):
        # Obtener la fecha enviada por parámetro GET "date"
        query_date = request.GET.get("date")

        # Validar el formato de la fecha o asignar fecha actual si no se pasa ninguna
        if query_date:
            try:
                # Validar que la fecha esté en formato YYYY-MM-DD
                datetime.strptime(query_date, "%Y-%m-%d")
            except ValueError:
                # Si la fecha es inválida, retornar error
                return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}
        else:
            # Si no se pasa fecha, usar la fecha local actual en formato YYYY-MM-DD
            query_date = localtime().date().strftime("%Y-%m-%d")

        # Consultar terapeutas con la cantidad de citas en la fecha indicada
        therapists = (
            Therapist.objects
            .annotate(
                # Anotar cada terapeuta con el conteo de citas filtradas por la fecha
                appointments_count=Count(
                    "appointments",
                    filter=Q(appointments__appointment_date=query_date)
                )
            )
            # Filtrar para quedarnos solo con terapeutas que tengan citas en esa fecha
            .filter(appointments_count__gt=0)
            # Solo seleccionar campos específicos para el resultado
            .values("id", "name", "paternal_lastname", "maternal_lastname", "appointments_count")
        )

        # Sumar el total de citas de todos los terapeutas en la fecha
        total_appointments = sum(t["appointments_count"] for t in therapists)

        # Retornar el listado de terapeutas con su conteo y el total general
        return {
            "therapists_appointments": list(therapists),
            "total_appointments_count": total_appointments
        }

    def get_patients_by_therapist(self, request):
        # Obtener fecha de parámetro GET "date"
        query_date = request.GET.get("date")

        # Si no se especifica la fecha, retornar error
        if not query_date:
            return {"error": "El parámetro date es obligatorio."}

        # Validar el formato de la fecha
        try:
            datetime.strptime(query_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}

        # Consultar citas para la fecha, que no estén marcadas como eliminadas (deleted_at is null)
        # y traer datos relacionados de paciente y terapeuta para evitar consultas adicionales
        appointments = (
            Appointment.objects
            .select_related("patient", "therapist")
            .filter(
                appointment_date=query_date,
                deleted_at__isnull=True
            )
        )

        # Diccionario donde se almacenará el reporte final agrupado por terapeuta
        report = {}

        # Estructura para pacientes que no tienen terapeuta asignado
        sin_terapeuta = {
            "therapist_id": "",
            "therapist": "Sin terapeuta asignado",
            "patients": {}
        }

        # Recorrer cada cita
        for appointment in appointments:
            patient = appointment.patient
            therapist = appointment.therapist

            # Si no hay paciente asignado, ignorar esa cita
            if not patient:
                continue

            # Datos básicos del paciente junto con un contador inicial de citas = 1
            patient_data = {
                "patient_id": patient.id,
                "patient": f"{patient.paternal_lastname} {patient.maternal_lastname} {patient.name}".strip(),
                "appointments": 1
            }

            if not therapist:
                # Si la cita no tiene terapeuta, agregar o actualizar en sin_terapeuta
                key = patient.id
                if key not in sin_terapeuta["patients"]:
                    sin_terapeuta["patients"][key] = patient_data
                else:
                    sin_terapeuta["patients"][key]["appointments"] += 1
            else:
                # Si tiene terapeuta, agregar o actualizar en report bajo el terapeuta correspondiente
                t_id = therapist.id
                if t_id not in report:
                    # Crear entrada para el terapeuta si no existe
                    report[t_id] = {
                        "therapist_id": t_id,
                        "therapist": f"{therapist.paternal_lastname} {therapist.maternal_lastname} {therapist.name}".strip(),
                        "patients": {}
                    }
                key = patient.id
                if key not in report[t_id]["patients"]:
                    report[t_id]["patients"][key] = patient_data
                else:
                    report[t_id]["patients"][key]["appointments"] += 1

        # Si hay pacientes sin terapeuta, agregarlos al reporte final
        if sin_terapeuta["patients"]:
            report["sinTherapist"] = sin_terapeuta

        # Convertir los diccionarios de pacientes a listas para facilitar manejo en frontend/JSON
        for therapist_id in report:
            report[therapist_id]["patients"] = list(report[therapist_id]["patients"].values())

        # Retornar la lista de terapeutas con sus pacientes y conteo de citas
        return list(report.values())

    def get_daily_cash(self, request):
        """
        Obtiene el resumen diario de efectivo agrupado por tipo de pago y monto total,
        ordenado específicamente: Cupón, EFECTIVO, Yape, Otros.
        """
        query_date = request.GET.get("date")

        if query_date:
            try:
                datetime.strptime(query_date, "%Y-%m-%d")
            except ValueError:
                return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}
        else:
            query_date = localtime().date().strftime("%Y-%m-%d")

        # Consulta: citas del día con pago, que no estén eliminadas
        payments = (
            Appointment.objects
            .filter(
                appointment_date=query_date,
                deleted_at__isnull=True,
                payment__isnull=False,
                payment_type__isnull=False,
            )
            .values('payment_type__name')
            .annotate(total_payment=models.Sum('payment'))
        )

        # Crear diccionario para ordenar segun orden requerido
        order = {"Cupón": 0, "EFECTIVO": 1, "Yape": 2}

        # Separar los que tienen nombre en orden y los otros
        pagos_ordenados = []
        otros = []

        for p in payments:
            tipo = p['payment_type__name']
            if tipo in order:
                pagos_ordenados.append(p)
            else:
                otros.append(p)

        # Ordenar pagos_ordenados según el orden definido
        pagos_ordenados.sort(key=lambda x: order[x['payment_type__name']])
        # Agregar al final los "otros"
        pagos_ordenados.extend(otros)

        # Cambiar estructura para mejor legibilidad, si quieres:
        result = [
            {
                "payment_type": p['payment_type__name'],
                "total_payment": float(p['total_payment'])
            }
            for p in pagos_ordenados
        ]

        return result

    def get_appointments_between_dates(self, request):
        """
        Obtiene todas las citas entre dos fechas dadas (inclusive),
        con información del paciente y terapeuta.
        """
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not start_date or not end_date:
            return {"error": "Parámetros start_date y end_date son obligatorios."}

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}

        appointments = (
            Appointment.objects
            .select_related("patient", "therapist")
            .filter(
                appointment_date__gte=start_date,
                appointment_date__lte=end_date,
                deleted_at__isnull=True
            )
            .order_by("appointment_date", "appointment_hour")
        )

        result = []
        for app in appointments:
            therapist_name = "Sin terapeuta asignado"
            if app.therapist:
                therapist_name = " ".join(filter(None, [
                    app.therapist.paternal_lastname,
                    app.therapist.maternal_lastname,
                    app.therapist.name
                ]))

            patient_name = "Paciente desconocido"
            if app.patient:
                patient_name = " ".join(filter(None, [
                    app.patient.paternal_lastname,
                    app.patient.maternal_lastname,
                    app.patient.name
                ]))

            result.append({
                "appointment_id": app.id,
                "appointment_date": app.appointment_date.strftime("%Y-%m-%d"),
                "appointment_hour": app.appointment_hour if isinstance(app.appointment_hour, str) else app.appointment_hour.strftime("%H:%M"),
                "therapist": therapist_name,
                "patient": patient_name,
                "payment": float(app.payment) if app.payment else 0,
                "payment_type": app.payment_type.name if app.payment_type else "No definido"
            })

        return result
