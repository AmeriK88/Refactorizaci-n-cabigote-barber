from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.decorators import handle_exceptions

from .forms import CitaForm
from .models import Cita
from services.models import Servicio
from .services.forms import apply_validation_error_to_form

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_date

from .services.availability import get_unavailable_start_hours_for_date

from .services.availability import (
    build_calendar_constraints,
    build_unavailable_by_service,
    normalize_booking_datetime,
    validate_datetime_for_booking,
)
from .services.notifications import (
    notify_booking_created,
    notify_booking_deleted,
    notify_booking_updated,
)


# APPOINTMENT RESERVATION
@login_required
@handle_exceptions
def reservar_cita(request, servicio_id=None):
    servicio_seleccionado = (
        Servicio.objects.filter(id=servicio_id).first() if servicio_id else None
    )

    def calendar_payload():
        fechas_ocupadas, fechas_bloqueadas, horas_ocupadas_por_fecha, bloqueos_por_fecha = (
            build_calendar_constraints()
        )
        return {
            "fechas_ocupadas": fechas_ocupadas,
            "fechas_bloqueadas": fechas_bloqueadas,
            "horas_ocupadas_por_fecha": horas_ocupadas_por_fecha,
            "bloqueos_por_fecha": bloqueos_por_fecha,
        }   

    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            fecha, hora, fecha_hora = normalize_booking_datetime(
                fecha=form.cleaned_data["fecha"],
                hora=form.cleaned_data["hora"],
            )

            try:
                service_minutes = int(
                    getattr(form.cleaned_data["servicio"], "duracion", 30) or 30
                )

                validate_datetime_for_booking(
                    fecha=fecha,
                    hora=hora,
                    fecha_hora=fecha_hora,
                    service_minutes=service_minutes,
                )

            except ValidationError as e:
                apply_validation_error_to_form(form, e)

            if not form.errors:
                cita = form.save(commit=False)
                cita.usuario = request.user
                cita.fecha = fecha_hora
                cita.hora = hora
                cita.save()

                # OJO: esto puede ser lento si manda email síncrono
                notify_booking_created(request.user.email, cita)

                messages.success(request, "¡Viejito! Ya tienes tu cita confirmada. ¡Esa es niñote!")
                return redirect("users:perfil_usuario")

        # Solo si hay errores y hay que re-renderizar, calculamos payload
        ctx = {"form": form, **calendar_payload()}
        return render(request, "appointments/reservar_cita.html", ctx)

    # GET
    initial = {"servicio": servicio_seleccionado} if servicio_seleccionado else {}
    form = CitaForm(initial=initial)
    ctx = {"form": form, **calendar_payload()}
    return render(request, "appointments/reservar_cita.html", ctx)



# APPOINTMENT HISTORY
@login_required
@handle_exceptions
def ver_citas(request):
    current_year = timezone.localdate().year

    years = [
        d.year
        for d in Cita.objects.filter(usuario=request.user).dates(
            "fecha", "year", order="DESC"
        )
    ]

    if current_year not in years:
        years = [current_year] + years

    try:
        selected_year = int(request.GET.get("year", current_year))
    except (TypeError, ValueError):
        selected_year = current_year

    if years and selected_year not in years:
        selected_year = years[0]

    citas_activas = (
        Cita.objects.filter(usuario=request.user, fecha__gte=timezone.now())
        .select_related("servicio")
        .order_by("fecha", "hora")
    )

    citas_pasadas_qs = (
        Cita.objects.filter(
            usuario=request.user,
            fecha__lt=timezone.now(),
            fecha__year=selected_year,
        )
        .select_related("servicio")
        .order_by("-fecha", "-hora")
    )

    total_gastado_year = (
        citas_pasadas_qs.aggregate(total=Sum("servicio__precio"))["total"] or 0
    )

    paginator = Paginator(citas_pasadas_qs, 18)
    page_number = request.GET.get("page")
    citas_pasadas = paginator.get_page(page_number)

    return render(
        request,
        "appointments/ver_citas.html",
        {
            "citas_activas": citas_activas,
            "citas_pasadas": citas_pasadas,
            "years": years,
            "selected_year": selected_year,
            "total_gastado_year": total_gastado_year,
        },
    )


# APPOINTMENT EDITING
@login_required
@handle_exceptions
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)

    if cita.fecha < timezone.now():
        messages.error(request, "¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.")
        return redirect("appointments:ver_citas")

    fechas_ocupadas, fechas_bloqueadas, horas_ocupadas_por_fecha, bloqueos_por_fecha = (
        build_calendar_constraints(exclude_cita_id=cita_id)
    )


    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            fecha, hora, fecha_hora = normalize_booking_datetime(
                fecha=form.cleaned_data["fecha"],
                hora=form.cleaned_data["hora"],
            )

            try:
                service_minutes = int(
                    getattr(form.cleaned_data["servicio"], "duracion", 30) or 30
                )

                validate_datetime_for_booking(
                    fecha=fecha,
                    hora=hora,
                    fecha_hora=fecha_hora,
                    service_minutes=service_minutes,
                    exclude_cita_id=cita_id,
                )

            except ValidationError as e:
                apply_validation_error_to_form(form, e)

            if not form.errors:
                cita = form.save(commit=False)
                cita.fecha = fecha_hora
                cita.hora = hora
                cita.save()

                notify_booking_updated(request.user.email, cita)
                messages.success(request, "¡Eres un puntal! Actualizaste tu cita.")
                return redirect("appointments:ver_citas")
    else:
        form = CitaForm(instance=cita)

    return render(
        request,
        "appointments/editar_cita.html",
        {
            "form": form,
            "cita": cita, 
            "fechas_ocupadas": fechas_ocupadas,
            "fechas_bloqueadas": fechas_bloqueadas,
            "horas_ocupadas_por_fecha": horas_ocupadas_por_fecha,
            "bloqueos_por_fecha": bloqueos_por_fecha,
        },
    )



# DELETE APPOINTMENT
@login_required
@handle_exceptions
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)

    if not cita.puede_cancelar():
        return render(
            request,
            "appointments/eliminar_cita.html",
            {
                "cita": cita,
                "error_message": "¡Mi niño! No puedes cancelar citas con 24hrs de antelación.",
            },
        )

    if request.method == "POST":
        cita_detalle = {
            "usuario": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
            "servicio": cita.servicio.nombre,
            "fecha": cita.fecha,
            "hora": cita.hora,
        }

        cita.delete()
        notify_booking_deleted(cita_detalle["email"], cita_detalle)
        messages.success(request, "¡Fuerte loco! Has cancelado tu cita.")
        return redirect("appointments:ver_citas")

    return render(request, "appointments/eliminar_cita.html", {"cita": cita})



@login_required
@require_GET
def availability_for_date(request):
    service_id = request.GET.get("service_id")
    date_str = request.GET.get("date")

    if not service_id or not date_str:
        return JsonResponse({"unavailable": []}, status=400)

    day = parse_date(date_str)
    if not day:
        return JsonResponse({"unavailable": []}, status=400)

    servicio = get_object_or_404(Servicio.objects.only("id", "duracion"), id=service_id)
    service_minutes = int(getattr(servicio, "duracion", 30) or 30)

    exclude_cita_id = request.GET.get("exclude_cita_id")
    exclude_cita_id = int(exclude_cita_id) if exclude_cita_id and exclude_cita_id.isdigit() else None

    unavailable = get_unavailable_start_hours_for_date(
        day=day,
        service_minutes=service_minutes,
        exclude_cita_id=exclude_cita_id,
    )
    return JsonResponse({"unavailable": unavailable})


# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.