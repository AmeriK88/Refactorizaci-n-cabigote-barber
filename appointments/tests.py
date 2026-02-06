from datetime import date, time, datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from appointments.models import FechaBloqueada, BloqueoHora
from appointments.services.availability import validate_datetime_for_booking

from appointments.models import Servicio, Cita
from appointments.services.availability import has_duration_conflict
from django.contrib.auth import get_user_model

from django.urls import reverse



class AvailabilityTests(TestCase):
    def test_fecha_bloqueada(self):
        hoy = date.today()
        FechaBloqueada.objects.create(fecha=hoy)

        fecha_hora = timezone.make_aware(datetime.combine(hoy, time(10, 0)))

        with self.assertRaises(ValidationError):
            validate_datetime_for_booking(
                fecha=hoy,
                hora=time(10, 0),
                fecha_hora=fecha_hora,
                service_minutes=30,
            )


    def test_hora_bloqueada(self):
        hoy = date.today()
        BloqueoHora.objects.create(
            fecha=hoy,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )

        fecha_hora = timezone.make_aware(datetime.combine(hoy, time(10, 0)))

        with self.assertRaises(ValidationError):
            validate_datetime_for_booking(
                fecha=hoy,
                hora=time(10, 0),
                fecha_hora=fecha_hora,
                service_minutes=30,
            )




class DurationConflictTests(TestCase):
    def test_conflict_by_duration(self):
        servicio_60 = Servicio.objects.create(nombre="Corte 60", precio=10, duracion=60)
        servicio_30 = Servicio.objects.create(nombre="Corte 30", precio=10, duracion=30)

        hoy = date.today()
        start_existing = timezone.make_aware(datetime.combine(hoy, time(10, 0)))
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="1234")

        Cita.objects.create(
            usuario=user,
            servicio=servicio_60,
            fecha=start_existing,
            hora=time(10, 0),
        )


        start_new = timezone.make_aware(datetime.combine(hoy, time(10, 30)))
        self.assertTrue(has_duration_conflict(
            fecha_hora_inicio=start_new,
            new_minutes=30,
        ))



class ViewsSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="smoke", password="1234")
        self.client.login(username="smoke", password="1234")

    def test_reservar_cita_loads(self):
        resp = self.client.get(reverse("appointments:reservar_cita"))
        self.assertEqual(resp.status_code, 200)

    def test_ver_citas_loads(self):
        resp = self.client.get(reverse("appointments:ver_citas"))
        self.assertEqual(resp.status_code, 200)
