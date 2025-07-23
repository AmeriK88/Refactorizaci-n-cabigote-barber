from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count
from .models import Cita, FechaBloqueada, Servicio, BloqueoHora
from .forms import CitaForm  
from core.utils import enviar_confirmacion_cita, enviar_notificacion_modificacion_cita, enviar_notificacion_eliminacion_cita
from core.decorators import handle_exceptions  

# APPOINTMENT RESERVATION
@login_required
@handle_exceptions
def reservar_cita(request, servicio_id=None):
    """
    Reserva una cita: controla fechas/horas bloqueadas
    y guarda un DateTimeField *aware* en `Cita.fecha`.
    """
    # ---------------- HORAS DISPONIBLES ----------------
    valid_hours_str = [h[0] for h in CitaForm.HORA_CHOICES if h[0]]

    # Fechas llenas
    horas_por_dia = (
        Cita.objects.filter(hora__in=valid_hours_str)           
        .values("fecha__date")
        .annotate(total_citas=Count("hora"))
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [e["fecha__date"].isoformat() for e in horas_por_dia]

    # Fechas bloqueadas
    fechas_bloqueadas = [
        f.isoformat() for f in FechaBloqueada.objects.values_list("fecha", flat=True)
    ]

    # Horas ocupadas
    horas_ocupadas_por_fecha = {}
    for c in Cita.objects.filter(hora__in=valid_hours_str):
        
        fecha_str = c.fecha.date().isoformat()
        horas_ocupadas_por_fecha.setdefault(fecha_str, []).append(c.hora.strftime("%H:%M"))

    # Horas bloqueadas por fecha
    bloqueos_por_fecha = {}
    for bloqueo in BloqueoHora.objects.all():
        fecha_str = bloqueo.fecha.isoformat()
        bloqueos_por_fecha.setdefault(fecha_str, [])
        for hour_str in valid_hours_str:
            opt_time = datetime.strptime(hour_str, "%H:%M").time()
            if bloqueo.hora_inicio <= opt_time < bloqueo.hora_fin:
                bloqueos_por_fecha[fecha_str].append(hour_str)

    # Pre-selección de servicio desde la URL
    servicio_seleccionado = (
        Servicio.objects.filter(id=servicio_id).first() if servicio_id else None
    )

    # ---------------- POST ----------------
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():

            fecha = form.cleaned_data["fecha"]  
            hora  = form.cleaned_data["hora"]   

            if isinstance(fecha, datetime):
                fecha = fecha.date()

            if isinstance(hora, str):
                hora = datetime.strptime(hora, "%H:%M").time()

            fecha_hora = timezone.make_aware(
                datetime.combine(fecha, hora),
                timezone.get_current_timezone(),
            )

            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error("fecha", "Esta fecha está bloqueada. Selecciona otra.")
            else:
                for bloqueo in BloqueoHora.objects.filter(fecha=fecha):
                    if bloqueo.hora_inicio <= hora < bloqueo.hora_fin:
                        form.add_error(
                            "hora",
                            f"La hora seleccionada está bloqueada "
                            f"({bloqueo.hora_inicio:%H:%M} - {bloqueo.hora_fin:%H:%M}).",
                        )
                        break

            # ---------- SAVE ----------
            if not form.errors:
                cita = form.save(commit=False)
                cita.usuario = request.user
                cita.fecha   = fecha_hora  
                cita.hora    = hora        
                cita.save()

                enviar_confirmacion_cita(request.user.email, cita)
                messages.success(
                    request,
                    "¡Viejito! Ya tienes tu cita confirmada. ¡Esa es niñote!",
                )
                return redirect("users:perfil_usuario")

    # ---------------- GET ----------------
    else:
        initial = {"servicio": servicio_seleccionado} if servicio_seleccionado else {}
        form = CitaForm(initial=initial)

    # ---------------- RENDER -------------
    return render(
        request,
        "appointments/reservar_cita.html",
        {
            "form": form,
            "fechas_ocupadas": fechas_ocupadas,
            "fechas_bloqueadas": fechas_bloqueadas,
            "horas_ocupadas_por_fecha": horas_ocupadas_por_fecha,
            "bloqueos_por_fecha": bloqueos_por_fecha,
        },
    )

# APPOINTMENT HISTORY
@login_required
@handle_exceptions
def ver_citas(request):
    citas_activas = Cita.objects.filter(
        usuario=request.user,
        fecha__gte=timezone.now()
    ).order_by('fecha', 'hora')
    
    citas_pasadas = Cita.objects.filter(
        usuario=request.user,
        fecha__lt=timezone.now()
    ).order_by('-fecha', '-hora') 

    return render(request, 'appointments/ver_citas.html', {
        'citas_activas': citas_activas,
        'citas_pasadas': citas_pasadas
    })

@login_required
@handle_exceptions
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)

    if cita.fecha < timezone.now():
        messages.error(request, "¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.")
        return redirect("appointments:ver_citas")

    # -------- 1) BLOCKED & OCCUPIED --------
    valid_hours_str = [h[0] for h in CitaForm.HORA_CHOICES if h[0]]

    horas_por_dia = (
        Cita.objects.filter(hora__in=valid_hours_str)
        .values("fecha__date")
        .annotate(total_citas=Count("hora"))
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [e["fecha__date"].isoformat() for e in horas_por_dia]

    fechas_bloqueadas = [
        f.isoformat() for f in FechaBloqueada.objects.values_list("fecha", flat=True)
    ]

    horas_ocupadas_por_fecha = {}
    for c in Cita.objects.filter(hora__in=valid_hours_str).exclude(id=cita_id):
        
        fecha_str = c.fecha.date().isoformat()
        horas_ocupadas_por_fecha.setdefault(fecha_str, []).append(c.hora.strftime("%H:%M"))

    bloqueos_por_fecha = {}
    for bloqueo in BloqueoHora.objects.all():
        fecha_str = bloqueo.fecha.isoformat()
        bloqueos_por_fecha.setdefault(fecha_str, [])
        for hour_str in valid_hours_str:
            opt_time = datetime.strptime(hour_str, "%H:%M").time()
            if bloqueo.hora_inicio <= opt_time < bloqueo.hora_fin:
                bloqueos_por_fecha[fecha_str].append(hour_str)

    # -------- 2) POST / GET --------
    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            fecha = form.cleaned_data["fecha"]  
            hora  = form.cleaned_data["hora"]  

            # Normaliza tipos
            if isinstance(fecha, datetime):
                fecha = fecha.date()
            if isinstance(hora, str):
                hora = datetime.strptime(hora, "%H:%M").time()

            fecha_hora = timezone.make_aware(
                datetime.combine(fecha, hora),
                timezone.get_current_timezone(),
            )

            # ---DATE VALIDATIONS---
            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error("fecha", "Esta fecha está bloqueada. Selecciona otra.")

            # --- DUPLICICATE CHECK
            elif Cita.objects.filter(fecha=fecha_hora).exclude(id=cita_id).exists():
                form.add_error(None, "Ya hay otra cita en esa fecha y hora.")

            # BLOCKED HOURS
            else:
                for bloqueo in BloqueoHora.objects.filter(fecha=fecha):
                    if bloqueo.hora_inicio <= hora < bloqueo.hora_fin:
                        form.add_error(
                            "hora",
                            f"La hora está bloqueada "
                            f"({bloqueo.hora_inicio:%H:%M} - {bloqueo.hora_fin:%H:%M}).",
                        )
                        break

            # SAVE
            if not form.errors:
                cita = form.save(commit=False)
                cita.fecha = fecha_hora
                cita.hora  = hora
                cita.save()

                enviar_notificacion_modificacion_cita(request.user.email, cita)
                messages.success(request, "¡Eres un puntal! Actualizaste tu cita.")
                return redirect("appointments:ver_citas")
    else:
        form = CitaForm(instance=cita)

    # -------- 3) RENDER --------
    return render(
        request,
        "appointments/editar_cita.html",
        {
            "form": form,
            "fechas_ocupadas": fechas_ocupadas,
            "fechas_bloqueadas": fechas_bloqueadas,
            "horas_ocupadas_por_fecha": horas_ocupadas_por_fecha,
            "bloqueos_por_fecha": bloqueos_por_fecha,
        },
    )


# DELETE APPOINTMENT
# ---------------------------------------------------
@login_required
@handle_exceptions
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    
    # CANCELLATION RESTRICTIONS
    if not cita.puede_cancelar():
        return render(request, 'appointments/eliminar_cita.html', {
            'cita': cita,
            'error_message': "¡Mi niño! No puedes cancelar citas con 24hrs de antelación."
        })

    if request.method == 'POST':
        cita_detalle = {
            'usuario' : request.user.get_full_name() or request.user.username,
            'email'   : request.user.email,
            'servicio': cita.servicio.nombre,
            'fecha'   : cita.fecha,
            'hora'    : cita.hora,
        }
        
        cita.delete()
        # SEND NOTIFICATION
        enviar_notificacion_eliminacion_cita(cita_detalle['email'], cita_detalle)
        messages.success(request, "¡Fuerte loco! Has cancelado tu cita.")
        return redirect('appointments:ver_citas')

    return render(request, 'appointments/eliminar_cita.html', {'cita': cita})

# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.