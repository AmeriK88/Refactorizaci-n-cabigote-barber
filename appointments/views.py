from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count
from .models import Cita, FechaBloqueada, Servicio 
from .forms import CitaForm  
from core.utils import enviar_confirmacion_cita, enviar_notificacion_modificacion_cita, enviar_notificacion_eliminacion_cita
from core.decorators import handle_exceptions  


@login_required
@handle_exceptions
def reservar_cita(request, servicio_id=None):
    # Listado de horas válidas (excluimos la de 'Seleccione una hora')
    valid_hours_str = [h[0] for h in CitaForm.HORA_CHOICES if h[0]]

    # Obtener fechas completamente reservadas
    horas_por_dia = (
        Cita.objects
        # Filtramos solo las citas con horas válidas
        .filter(hora__in=valid_hours_str)
        .values('fecha__date')
        .annotate(total_citas=Count('hora'))
        # Marcamos “día completo” si tiene todas las horas válidas ocupadas
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [entry['fecha__date'].isoformat() for entry in horas_por_dia]

    # Obtener fechas bloqueadas
    fechas_bloqueadas = FechaBloqueada.objects.values_list('fecha', flat=True)
    fechas_bloqueadas = [fecha.isoformat() for fecha in fechas_bloqueadas]

    # Crear un diccionario de horas ocupadas por fecha
    horas_ocupadas_por_fecha = {}
    for cita_existente in Cita.objects.filter(hora__in=valid_hours_str):
        fecha_str = cita_existente.fecha.date().isoformat()
        hora_str = cita_existente.hora.strftime("%H:%M")
        if fecha_str not in horas_ocupadas_por_fecha:
            horas_ocupadas_por_fecha[fecha_str] = []
        horas_ocupadas_por_fecha[fecha_str].append(hora_str)

    servicio_seleccionado = None
    if servicio_id:
        servicio_seleccionado = Servicio.objects.filter(id=servicio_id).first()

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hora = form.cleaned_data['hora']
            fecha_hora = datetime.combine(fecha, hora)
            fecha_hora = timezone.make_aware(fecha_hora)

            # Revisamos si la fecha está bloqueada
            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error('fecha', 'Esta fecha está bloqueada. Por favor, selecciona otra fecha.')
            else:
                # Guardamos la cita
                cita = form.save(commit=False)
                cita.usuario = request.user
                cita.fecha = fecha_hora
                cita.hora = hora  # Ojo, asignación para que quede registrada la hora
                cita.save()

                # Notificamos y mostramos mensaje de éxito
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
        'horas_ocupadas_por_fecha': horas_ocupadas_por_fecha
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

    # Listado de horas válidas (excluimos la de 'Seleccione una hora')
    valid_hours_str = [h[0] for h in CitaForm.HORA_CHOICES if h[0]]

    # Obtener fechas completamente reservadas (mismo enfoque que reservar_cita)
    horas_por_dia = (
        Cita.objects
        .filter(hora__in=valid_hours_str)
        .values('fecha__date')
        .annotate(total_citas=Count('hora'))
        .filter(total_citas=len(valid_hours_str))
    )
    fechas_ocupadas = [entry['fecha__date'].isoformat() for entry in horas_por_dia]

    # Obtener fechas bloqueadas
    fechas_bloqueadas = FechaBloqueada.objects.values_list('fecha', flat=True)
    fechas_bloqueadas = [fecha.isoformat() for fecha in fechas_bloqueadas]

    # Crear un diccionario de horas ocupadas por fecha
    horas_ocupadas_por_fecha = {}
    for cita_existente in Cita.objects.filter(hora__in=valid_hours_str):
        fecha_str = cita_existente.fecha.date().isoformat()
        hora_str = cita_existente.hora.strftime("%H:%M")
        if fecha_str not in horas_ocupadas_por_fecha:
            horas_ocupadas_por_fecha[fecha_str] = []
        horas_ocupadas_por_fecha[fecha_str].append(hora_str)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hora = form.cleaned_data['hora']
            fecha_hora = timezone.make_aware(datetime.combine(fecha, hora))

            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error('fecha', 'Esta fecha está bloqueada. Por favor, selecciona otra fecha.')
            elif Cita.objects.filter(fecha=fecha_hora).exclude(id=cita_id).exists():
                form.add_error(None, "Ya existe una cita reservada en esa fecha y hora.")
            else:
                # Actualizar el objeto Cita con la nueva fecha/hora y guardarlo
                cita = form.save(commit=False)
                cita.fecha = fecha_hora
                cita.hora = hora  # Aseguramos la hora en el TimeField
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
        'horas_ocupadas_por_fecha': horas_ocupadas_por_fecha
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