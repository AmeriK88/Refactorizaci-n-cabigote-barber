from datetime import date, time, datetime
from datetime import timedelta as dt_timedelta
import re

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from appointments.models import FechaBloqueada, BloqueoHora
from appointments.services.availability import validate_datetime_for_booking

from .models import Cita
from services.models import Servicio

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
        self.client.force_login(self.user)

    def test_reservar_cita_loads(self):
        resp = self.client.get(reverse("appointments:reservar_cita"))
        self.assertEqual(resp.status_code, 200)

    def test_ver_citas_loads(self):
        resp = self.client.get(reverse("appointments:ver_citas"))
        self.assertEqual(resp.status_code, 200)


class DescargarCitaICSTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", password="1234")
        self.other = User.objects.create_user(username="other", password="1234")

        self.servicio = Servicio.objects.create(
            nombre="Corte Premium",
            descripcion="Corte con acabado",
            precio=18,
            duracion=45,
        )

        cita_start = timezone.now() + dt_timedelta(days=2)
        cita_start = timezone.localtime(cita_start).replace(second=0, microsecond=0)

        self.cita_owner = Cita.objects.create(
            usuario=self.owner,
            servicio=self.servicio,
            fecha=cita_start,
            hora=cita_start.time(),
            comentario="Llevar referencia de corte",
        )

        self.url_owner = reverse("appointments:descargar_cita_ics", args=[self.cita_owner.id])

    def test_usuario_autenticado_descarga_su_cita(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url_owner)
        self.assertEqual(response.status_code, 200)

    def test_usuario_no_puede_descargar_cita_ajena(self):
        self.client.force_login(self.other)
        response = self.client.get(self.url_owner)
        self.assertEqual(response.status_code, 404)

    def test_response_content_type_calendar(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url_owner)
        self.assertTrue(response["Content-Type"].startswith("text/calendar"))

    def test_response_contiene_bloque_vcalendar(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url_owner)
        content = response.content.decode("utf-8")
        self.assertIn("BEGIN:VCALENDAR", content)
        self.assertIn("END:VCALENDAR", content)

    def test_evento_contiene_fecha_hora_y_titulo(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url_owner)
        content = response.content.decode("utf-8")

        self.assertIn("SUMMARY:Corte Premium", content)
        self.assertRegex(content, r"DTSTART;TZID=Atlantic/Canary:\d{8}T\d{6}")
        self.assertRegex(content, r"DTEND;TZID=Atlantic/Canary:\d{8}T\d{6}")

    def test_duracion_servicio_se_aplica_en_dtend(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url_owner)
        content = response.content.decode("utf-8")

        dtstart_match = re.search(r"DTSTART;TZID=Atlantic/Canary:(\d{8}T\d{6})", content)
        dtend_match = re.search(r"DTEND;TZID=Atlantic/Canary:(\d{8}T\d{6})", content)

        self.assertIsNotNone(dtstart_match)
        self.assertIsNotNone(dtend_match)

        start = datetime.strptime(dtstart_match.group(1), "%Y%m%dT%H%M%S")
        end = datetime.strptime(dtend_match.group(1), "%Y%m%dT%H%M%S")
        self.assertEqual(int((end - start).total_seconds() / 60), 45)


class VerCitasEnhancementsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="miscitas", password="1234")
        self.client.force_login(self.user)

        self.servicio = Servicio.objects.create(
            nombre="Corte Fade",
            descripcion="Corte moderno",
            precio=16,
            duracion=40,
        )

        active_day = timezone.localdate() + dt_timedelta(days=3)
        active_dt = timezone.make_aware(datetime.combine(active_day, time(12, 30)))
        self.cita_activa = Cita.objects.create(
            usuario=self.user,
            servicio=self.servicio,
            fecha=active_dt,
            hora=time(12, 30),
            comentario="Activo",
        )

        past_day = timezone.localdate() - dt_timedelta(days=30)
        past_dt = timezone.make_aware(datetime.combine(past_day, time(10, 0)))
        self.cita_pasada = Cita.objects.create(
            usuario=self.user,
            servicio=self.servicio,
            fecha=past_dt,
            hora=time(10, 0),
            comentario="Pasado",
        )

    def test_ver_citas_activa_muestra_dias_restantes_y_boton_calendario(self):
        response = self.client.get(reverse("appointments:ver_citas"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Faltan 3 días")
        self.assertContains(response, "Guardar en mi calendario")
        self.assertContains(
            response,
            reverse("appointments:descargar_cita_ics", args=[self.cita_activa.id]),
        )
        self.assertNotContains(response, "Pendiente")
        self.assertContains(response, "Cancelar")

    def test_historial_muestra_reservar_de_nuevo_con_servicio(self):
        response = self.client.get(reverse("appointments:ver_citas"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservar de nuevo")
        self.assertContains(
            response,
            reverse("appointments:reservar_cita_servicio", args=[self.servicio.id]),
        )

    def test_reservar_con_servicio_id_precarga_servicio(self):
        response = self.client.get(
            reverse("appointments:reservar_cita_servicio", args=[self.servicio.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context["form"]["servicio"].value()), str(self.servicio.id))

    def test_reservar_normal_sin_servicio_id_sigue_funcionando(self):
        response = self.client.get(reverse("appointments:reservar_cita"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.context["form"]["servicio"].value(), (None, "", []))
