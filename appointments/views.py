from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count
from django.utils.html import format_html
import base64
import matplotlib.pyplot as plt
import io
import urllib

from .models import Cita, FechaBloqueada  
from .forms import CitaForm  
from core.utils import enviar_confirmacion_cita  
from core.utils import enviar_notificacion_modificacion_cita
from core.utils import enviar_notificacion_eliminacion_cita
from core.decorators import handle_exceptions  

@login_required
@handle_exceptions
def reservar_cita(request):
    # Obtener fechas completamente reservadas
    horas_por_dia = Cita.objects.values('fecha__date').annotate(total_citas=Count('hora')).filter(total_citas=len(CitaForm.HORA_CHOICES) - 1)
    fechas_ocupadas = [entry['fecha__date'].isoformat() for entry in horas_por_dia]

    # Obtener fechas bloqueadas
    fechas_bloqueadas = FechaBloqueada.objects.values_list('fecha', flat=True)
    fechas_bloqueadas = [fecha.isoformat() for fecha in fechas_bloqueadas]

    # Crear un diccionario de horas ocupadas por fecha
    citas = Cita.objects.all()
    horas_ocupadas_por_fecha = {cita.fecha.date().isoformat(): [] for cita in citas}
    for cita in citas:
        horas_ocupadas_por_fecha[cita.fecha.date().isoformat()].append(cita.fecha.strftime("%H:%M"))

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hora = form.cleaned_data['hora']
            fecha_hora = timezone.make_aware(datetime.combine(fecha, hora))

            if fecha.isoformat() in fechas_bloqueadas:
                form.add_error('fecha', 'Esta fecha está bloqueada. Por favor, selecciona otra fecha.')
            else:
                cita = form.save(commit=False)
                cita.usuario = request.user
                cita.fecha = fecha_hora
                cita.save()
                enviar_confirmacion_cita(request.user.email, cita)
                messages.success(request, '¡Viejito! Ya tienes tu cita confirmada ¡Esa es niñote!.')
                return redirect('users:perfil_usuario')
    else:
        form = CitaForm()

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
    citas_activas = Cita.objects.filter(usuario=request.user, fecha__gte=timezone.now())  
    citas_pasadas = Cita.objects.filter(usuario=request.user, fecha__lt=timezone.now()) 
    return render(request, 'appointments/ver_citas.html', {
        'citas_activas': citas_activas,
        'citas_pasadas': citas_pasadas
    })


# Editar citas según disponibilidad & manejo excepciones
@login_required
@handle_exceptions
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)
    
    if cita.fecha < timezone.now():
        messages.error(request, '¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.')
        return redirect('appointments:ver_citas')

    horas_por_dia = Cita.objects.values('fecha__date').annotate(total_citas=Count('hora')).filter(total_citas=len(CitaForm.HORA_CHOICES))
    fechas_ocupadas = [entry['fecha__date'].isoformat() for entry in horas_por_dia]
    fechas_bloqueadas = FechaBloqueada.objects.values_list('fecha', flat=True)
    fechas_bloqueadas = [fecha.isoformat() for fecha in fechas_bloqueadas]

    horas_ocupadas_por_fecha = {cita_existente.fecha.date().isoformat(): [] for cita_existente in Cita.objects.all()}
    for cita_existente in Cita.objects.all():
        horas_ocupadas_por_fecha[cita_existente.fecha.date().isoformat()].append(cita_existente.fecha.strftime("%H:%M"))

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
                cita.fecha = fecha_hora
                form.save()
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
