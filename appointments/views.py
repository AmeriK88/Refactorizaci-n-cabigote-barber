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


@login_required
@handle_exceptions
def reservar_cita(request, servicio_id=None):
    """
    View to reserve an appointment.
    
    In addition to checking occupied dates and blocked dates,
    this view now also computes blocked hours (via BloqueoHora)
    so that the template can disable hour choices that are blocked.
    """
    # List of valid hour strings (excluding the empty "Select an hour" option)
    valid_hours_str = [h[0] for h in CitaForm.HORA_CHOICES if h[0]]

    # Get completely reserved dates
    horas_por_dia = (
        Cita.objects
        .filter(hora__in=valid_hours_str)
        .values('fecha__date')
        .annotate(total_citas=Count('hora'))
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [entry['fecha__date'].isoformat() for entry in horas_por_dia]

    # Get blocked dates
    fechas_bloqueadas = FechaBloqueada.objects.values_list('fecha', flat=True)
    fechas_bloqueadas = [fecha.isoformat() for fecha in fechas_bloqueadas]

    # Build dictionary with occupied hours per date
    horas_ocupadas_por_fecha = {}
    for cita_existente in Cita.objects.filter(hora__in=valid_hours_str):
        fecha_str = cita_existente.fecha.date().isoformat()
        hora_str = cita_existente.hora.strftime("%H:%M")
        if fecha_str not in horas_ocupadas_por_fecha:
            horas_ocupadas_por_fecha[fecha_str] = []
        horas_ocupadas_por_fecha[fecha_str].append(hora_str)

    # Build dictionary with blocked hours per date from BloqueoHora
    bloqueos_por_fecha = {}
    bloqueos = BloqueoHora.objects.all()
    for bloqueo in bloqueos:
        fecha_str = bloqueo.fecha.isoformat()
        if fecha_str not in bloqueos_por_fecha:
            bloqueos_por_fecha[fecha_str] = []
        # For each valid hour option, check if it lies within the block range.
        for hour_str in valid_hours_str:
            # Convert hour string (e.g., "10:00") to time
            try:
                option_time = datetime.strptime(hour_str, '%H:%M').time()
            except Exception:
                continue
            # If the option time is in the blocked range, add it.
            if bloqueo.hora_inicio <= option_time < bloqueo.hora_fin:
                if hour_str not in bloqueos_por_fecha[fecha_str]:
                    bloqueos_por_fecha[fecha_str].append(hour_str)

    servicio_seleccionado = None
    if servicio_id:
        servicio_seleccionado = Servicio.objects.filter(id=servicio_id).first()

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hora = form.cleaned_data['hora']
            # Combine date and time and make timezone-aware
            fecha_hora = datetime.combine(fecha, hora)
            fecha_hora = timezone.make_aware(fecha_hora)

            # Check if the date is blocked
            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error('fecha', 'Esta fecha está bloqueada. Por favor, selecciona otra fecha.')
            else:
                # Check if the chosen hour falls within any blocked hour range for that date
                bloqueos = BloqueoHora.objects.filter(fecha=fecha)
                for bloqueo in bloqueos:
                    if bloqueo.hora_inicio <= hora < bloqueo.hora_fin:
                        form.add_error('hora', f"La hora seleccionada está bloqueada ({bloqueo.hora_inicio.strftime('%H:%M')} - {bloqueo.hora_fin.strftime('%H:%M')}).")
                        break

            if not form.errors:
                # Save the appointment
                cita = form.save(commit=False)
                cita.usuario = request.user
                cita.fecha = fecha_hora
                cita.hora = hora  # Ensure the time is registered
                cita.save()

                # Send confirmation and display success message
                enviar_confirmacion_cita(request.user.email, cita)
                messages.success(request, '¡Viejito! Ya tienes tu cita confirmada ¡Esa es niñote!.')
                return redirect('users:perfil_usuario')
    else:
        initial_data = {'servicio': servicio_seleccionado} if servicio_seleccionado else {}
        form = CitaForm(initial=initial_data)

    return render(request, 'appointments/reservar_cita.html', {
        'form': form,
        'fechas_ocupadas': fechas_ocupadas,
        'fechas_bloqueadas': fechas_bloqueadas,
        'horas_ocupadas_por_fecha': horas_ocupadas_por_fecha,
        'bloqueos_por_fecha': bloqueos_por_fecha  # Pass the blocked hours dictionary to the template
    })

# Función ver citas & historial
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
        messages.error(request, '¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.')
        return redirect('appointments:ver_citas')

    # List of valid hour strings (excluding the "Seleccione una hora" option)
    valid_hours_str = [h[0] for h in CitaForm.HORA_CHOICES if h[0]]

    # Get completely reserved dates (similar to reservar_cita)
    horas_por_dia = (
        Cita.objects
        .filter(hora__in=valid_hours_str)
        .values('fecha__date')
        .annotate(total_citas=Count('hora'))
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [entry['fecha__date'].isoformat() for entry in horas_por_dia]

    # Get blocked dates
    fechas_bloqueadas = FechaBloqueada.objects.values_list('fecha', flat=True)
    fechas_bloqueadas = [fecha.isoformat() for fecha in fechas_bloqueadas]

    # Build a dictionary with occupied hours per date
    horas_ocupadas_por_fecha = {}
    for cita_existente in Cita.objects.filter(hora__in=valid_hours_str):
        fecha_str = cita_existente.fecha.date().isoformat()
        hora_str = cita_existente.hora.strftime("%H:%M")
        if fecha_str not in horas_ocupadas_por_fecha:
            horas_ocupadas_por_fecha[fecha_str] = []
        horas_ocupadas_por_fecha[fecha_str].append(hora_str)

    # Build dictionary for blocked hours per date from BloqueoHora
    bloqueos_por_fecha = {}
    bloqueos = BloqueoHora.objects.all()
    for bloqueo in bloqueos:
        fecha_str = bloqueo.fecha.isoformat()
        if fecha_str not in bloqueos_por_fecha:
            bloqueos_por_fecha[fecha_str] = []
        for hour_str in valid_hours_str:
            try:
                option_time = datetime.strptime(hour_str, '%H:%M').time()
            except Exception:
                continue
            if bloqueo.hora_inicio <= option_time < bloqueo.hora_fin:
                if hour_str not in bloqueos_por_fecha[fecha_str]:
                    bloqueos_por_fecha[fecha_str].append(hour_str)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hora = form.cleaned_data['hora']
            fecha_hora = timezone.make_aware(datetime.combine(fecha, hora))

            # Check if the date is blocked
            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error('fecha', 'Esta fecha está bloqueada. Por favor, selecciona otra fecha.')
            # Check if another appointment already exists for the same date/time (excluding the current one)
            elif Cita.objects.filter(fecha=fecha_hora).exclude(id=cita_id).exists():
                form.add_error(None, "Ya existe una cita reservada en esa fecha y hora.")
            else:
                # NEW: Check if the chosen hour falls within any blocked hour range for that date
                bloqueos = BloqueoHora.objects.filter(fecha=fecha)
                for bloqueo in bloqueos:
                    if bloqueo.hora_inicio <= hora < bloqueo.hora_fin:
                        form.add_error('hora', f"La hora seleccionada está bloqueada ({bloqueo.hora_inicio.strftime('%H:%M')} - {bloqueo.hora_fin.strftime('%H:%M')}).")
                        break

            if form.is_valid():
                cita = form.save(commit=False)
                cita.fecha = fecha_hora
                cita.hora = hora
                cita.save()

                enviar_notificacion_modificacion_cita(request.user.email, cita)
                messages.success(request, '¡Eres un puntal! Actualizaste tu cita.')
                return redirect('appointments:ver_citas')
    else:
        form = CitaForm(instance=cita)

    return render(request, 'appointments/editar_cita.html', {
        'form': form,
        'fechas_ocupadas': fechas_ocupadas,
        'fechas_bloqueadas': fechas_bloqueadas,
        'horas_ocupadas_por_fecha': horas_ocupadas_por_fecha,
        'bloqueos_por_fecha': bloqueos_por_fecha  # Pass blocked hours dictionary for JavaScript
    })


# Función para eliminar cita & manejo excepciones
@login_required
@handle_exceptions
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    
    # Si la cita no se puede cancelar
    if not cita.puede_cancelar():
        return render(request, 'appointments/eliminar_cita.html', {
            'cita': cita,
            'error_message': "¡Mi niño! No puedes cancelar citas con 24hrs de antelación."
        })

    if request.method == 'POST':
        cita_detalle = {
            'email': request.user.email,
            'servicio': cita.servicio.nombre,
            'fecha': cita.fecha,
            'hora': cita.hora
        }
        
        cita.delete()
        # Enviar notificación de eliminación y mostrar mensaje de éxito
        enviar_notificacion_eliminacion_cita(cita_detalle['email'], cita_detalle)
        messages.success(request, "¡Fuerte loco! Has cancelado tu cita.")
        return redirect('appointments:ver_citas')

    return render(request, 'appointments/eliminar_cita.html', {'cita': cita})

# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.