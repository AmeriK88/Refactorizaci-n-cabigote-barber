from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Cita
from services.models import Servicio


class PerfilUsuarioCitasActivasTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username="perfil_user", password="1234")
		self.client.force_login(self.user)

		self.servicio = Servicio.objects.create(
			nombre="Corte Clasico",
			descripcion="Corte y peinado",
			precio=15,
			duracion=30,
		)

		target_date = timezone.localdate() + timedelta(days=3)
		cita_start = timezone.make_aware(datetime.combine(target_date, time(12, 0)))

		self.cita = Cita.objects.create(
			usuario=self.user,
			servicio=self.servicio,
			fecha=cita_start,
			hora=time(12, 0),
			comentario="Sin maquinilla",
		)

	def test_perfil_muestra_texto_dias_y_no_muestra_pendiente(self):
		response = self.client.get(reverse("users:perfil_usuario"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Faltan 3 días")
		self.assertNotContains(response, "Pendiente")

	def test_descarga_ics_sigue_funcionando_desde_cita_activa(self):
		response = self.client.get(
			reverse("appointments:descargar_cita_ics", args=[self.cita.id])
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response["Content-Type"].startswith("text/calendar"))
		self.assertIn("BEGIN:VCALENDAR", response.content.decode("utf-8"))
