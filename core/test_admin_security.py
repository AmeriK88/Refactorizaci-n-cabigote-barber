import datetime as dt
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from appointments.models import Cita
from core.tests import STATIC_STORAGES
from reports.models import ReporteDiario, ReporteMensual
from services.models import Servicio

PASSWORD = "Sec-pass-12345"  # nosec - credencial de prueba


def grant(user, *codenames):
    user.user_permissions.add(*Permission.objects.filter(codename__in=codenames))


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class AdminSecurityBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser("root", "root@example.com", PASSWORD)
        cls.plain = User.objects.create_user("plain", "plain@example.com", PASSWORD)
        cls.staff0 = User.objects.create_user("staff0", "s0@example.com", PASSWORD, is_staff=True)
        cls.viewer = User.objects.create_user("viewer", "v@example.com", PASSWORD, is_staff=True)
        grant(cls.viewer, "view_cita", "view_servicio", "view_user", "view_reportemensual")
        cls.editor = User.objects.create_user("editor", "e@example.com", PASSWORD, is_staff=True)
        grant(cls.editor, "view_reportemensual", "add_reportemensual", "change_reportemensual")
        cls.client_user = User.objects.create_user("cliente", "c@example.com", PASSWORD)

        cls.servicio = Servicio.objects.create(
            nombre="Corte", descripcion="d", precio=Decimal("15.00"), duracion=30
        )
        now = timezone.localtime()
        cls.cita = Cita.objects.create(
            usuario=cls.client_user, servicio=cls.servicio, fecha=now, hora=now.time()
        )

    def login(self, user, client=None):
        client = client or self.client
        client.force_login(user)
        return client

    def kpis(self, response):
        return response.context["citas_hoy"], response.context["servicios_total"], response.context["usuarios_total"]


class DashboardKpiPermissionTests(AdminSecurityBase):
    url = "/en/admin/"

    def test_anonymous_and_non_staff_get_login_without_kpis(self):
        for user in (None, self.plain):
            client = Client()
            if user:
                client.force_login(user)
            html = client.get(self.url).content.decode()
            self.assertNotIn("metric-card", html)
            self.assertNotIn("Citas hoy", html)

    def test_staff_without_permissions_receives_no_kpis(self):
        self.login(self.staff0)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(self.kpis(response), (None, None, None))
        self.assertIsNone(ctx["valor_estimado_hoy"])
        html = response.content.decode()
        for text in ("metric-card", "dashboard-cards", "Citas hoy", "Valor estimado", "btn-admin-action"):
            self.assertNotIn(text, html)

    def test_staff_without_permissions_does_not_query_restricted_tables(self):
        self.login(self.staff0)
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as queries:
            self.client.get(self.url)
        sql = " ".join(q["sql"] for q in queries)
        self.assertNotIn("appointments_cita", sql)
        self.assertNotIn("services_servicio", sql)

    def test_each_kpi_requires_its_own_permission(self):
        User = get_user_model()
        cases = {
            "view_cita": (1, None, None),
            "view_servicio": (None, 1, None),
            "view_user": (None, None, User.objects.count()),
        }
        for codename, expected in cases.items():
            with self.subTest(codename):
                user = User.objects.create_user(f"u_{codename}", password=PASSWORD, is_staff=True)
                grant(user, codename)
                if codename == "view_user":
                    expected = (None, None, User.objects.count())
                self.login(user)
                response = self.client.get(self.url)
                self.assertEqual(self.kpis(response), expected)
                html = response.content.decode()
                self.assertEqual("Valor estimado de reservas" in html, codename == "view_cita")

    def test_change_permission_also_counts_as_consult(self):
        User = get_user_model()
        user = User.objects.create_user("changer", password=PASSWORD, is_staff=True)
        grant(user, "change_cita")
        self.login(user)
        self.assertEqual(self.client.get(self.url).context["citas_hoy"], 1)

    def test_superuser_sees_everything(self):
        self.login(self.superuser)
        response = self.client.get(self.url)
        citas, servicios, usuarios = self.kpis(response)
        self.assertEqual((citas, servicios), (1, 1))
        self.assertEqual(usuarios, get_user_model().objects.count())
        self.assertEqual(response.context["valor_estimado_hoy"], Decimal("15.00"))
        self.assertIn("€15.00", response.content.decode())

    def test_restricted_values_are_not_leaked_in_html(self):
        self.login(self.staff0)
        html = self.client.get(self.url).content.decode()
        self.assertNotIn("15.00", html)


class DashboardQuickActionTests(AdminSecurityBase):
    url = "/en/admin/"

    def links(self, user):
        self.login(user)
        html = self.client.get(self.url).content.decode()
        return {
            "informe": f'href="{reverse("admin:descargar_reporte")}"' in html,
            "hoy": f'href="{reverse("admin:appointments_cita_changelist_hoy")}"' in html,
            "manana": f'href="{reverse("admin:appointments_cita_changelist_manana")}"' in html,
            "usuarios": f'href="{reverse("admin:auth_user_changelist")}"' in html,
        }

    def test_staff_without_permissions_sees_no_actions(self):
        self.assertFalse(any(self.links(self.staff0).values()))

    def test_viewer_sees_all_and_destinations_are_accessible(self):
        links = self.links(self.viewer)
        self.assertTrue(all(links.values()))
        for url in (
            reverse("admin:descargar_reporte"),
            reverse("admin:appointments_cita_changelist"),
            reverse("admin:auth_user_changelist"),
        ):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for url in (
            reverse("admin:appointments_cita_changelist_hoy"),
            reverse("admin:appointments_cita_changelist_manana"),
        ):
            self.assertEqual(self.client.get(url).status_code, 302, url)

    def test_report_only_user_sees_only_report_link(self):
        self.assertEqual(
            self.links(self.editor),
            {"informe": True, "hoy": False, "manana": False, "usuarios": False},
        )

    def test_add_permission_alone_does_not_show_consult_links(self):
        User = get_user_model()
        user = User.objects.create_user("adder", password=PASSWORD, is_staff=True)
        grant(user, "add_cita", "add_user")
        self.assertFalse(any(self.links(user).values()))


class CitaCustomEndpointTests(AdminSecurityBase):
    names = ("cita_dashboard", "cita_graph", "cita_graph_data",
             "appointments_cita_changelist_hoy", "appointments_cita_changelist_manana")

    def urls(self):
        return [reverse(f"admin:{n}") for n in self.names]

    def test_anonymous_is_redirected_to_login_without_content(self):
        for url in self.urls():
            response = Client().get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn("login", response["Location"])

    def test_non_staff_is_redirected_to_login(self):
        client = self.login(self.plain, Client())
        for url in self.urls():
            response = client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn("login", response["Location"])

    def test_staff_without_permission_gets_403_and_no_data(self):
        self.login(self.staff0)
        for url in self.urls():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403, url)
            self.assertNotIn(b'"counts"', response.content)
            self.assertNotIn(b"data:image/png", response.content)

    def test_view_permission_allows_all(self):
        self.login(self.viewer)
        data = self.client.get(reverse("admin:cita_graph_data"))
        self.assertEqual(data.status_code, 200)
        self.assertEqual(sum(data.json()["counts"]), 1)
        self.assertEqual(self.client.get(reverse("admin:cita_dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:cita_graph")).status_code, 200)

    def test_superuser_allowed(self):
        self.login(self.superuser)
        for url in self.urls():
            self.assertIn(self.client.get(url).status_code, (200, 302), url)

    def test_other_model_permission_is_not_enough(self):
        self.login(self.editor)
        self.assertEqual(self.client.get(reverse("admin:cita_graph_data")).status_code, 403)


class ReportPermissionPolicyTests(AdminSecurityBase):
    def test_no_unconditional_add_or_delete(self):
        self.login(self.staff0)
        self.assertEqual(self.client.get(reverse("admin:reports_reportemensual_add")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:reports_reportediario_add")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:reports_reportemensual_changelist")).status_code, 403)

    def test_post_add_without_permission_creates_nothing(self):
        self.login(self.staff0)
        r1 = self.client.post(reverse("admin:reports_reportemensual_add"), {"mes": "2030-01-01"})
        r2 = self.client.post(reverse("admin:reports_reportediario_add"), {"dia": "2030-01-01"})
        self.assertEqual((r1.status_code, r2.status_code), (403, 403))
        self.assertFalse(ReporteMensual.objects.exists())
        self.assertFalse(ReporteDiario.objects.exists())

    def test_delete_without_permission_is_rejected(self):
        mensual = ReporteMensual.objects.create(mes=dt.date(2030, 1, 1))
        diario = ReporteDiario.objects.create(dia=dt.date(2030, 1, 1))
        for user in (self.staff0, self.viewer, self.editor):
            self.login(user)
            r1 = self.client.post(reverse("admin:reports_reportemensual_delete", args=[mensual.pk]), {"post": "yes"})
            r2 = self.client.post(reverse("admin:reports_reportediario_delete", args=[diario.pk]), {"post": "yes"})
            self.assertEqual((r1.status_code, r2.status_code), (403, 403), user.username)
        self.assertTrue(ReporteMensual.objects.filter(pk=mensual.pk).exists())
        self.assertTrue(ReporteDiario.objects.filter(pk=diario.pk).exists())

    def test_bulk_delete_action_without_permission_is_rejected(self):
        mensual = ReporteMensual.objects.create(mes=dt.date(2030, 1, 1))
        self.login(self.viewer)
        response = self.client.post(
            reverse("admin:reports_reportemensual_changelist"),
            {"action": "delete_selected", "_selected_action": [mensual.pk], "post": "yes"},
        )
        self.assertIn(response.status_code, (200, 403))
        self.assertTrue(ReporteMensual.objects.filter(pk=mensual.pk).exists())

    def test_authorized_delete_and_add_work(self):
        User = get_user_model()
        user = User.objects.create_user("full", password=PASSWORD, is_staff=True)
        grant(user, "view_reportemensual", "add_reportemensual", "change_reportemensual", "delete_reportemensual")
        self.login(user)
        response = self.client.post(reverse("admin:reports_reportemensual_add"), {"mes": "2030-02-01"})
        self.assertEqual(response.status_code, 302)
        obj = ReporteMensual.objects.get(mes=dt.date(2030, 2, 1))
        response = self.client.post(reverse("admin:reports_reportemensual_delete", args=[obj.pk]), {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ReporteMensual.objects.filter(pk=obj.pk).exists())


class ReportDownloadTests(AdminSecurityBase):
    url_name = "admin:descargar_reporte"

    def test_anonymous_and_non_staff_redirected(self):
        for client in (Client(), self.login(self.plain, Client())):
            response = client.get(reverse(self.url_name))
            self.assertEqual(response.status_code, 302)
            self.assertIn("login", response["Location"])

    def test_staff_without_permission_gets_403(self):
        self.login(self.staff0)
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(b"Ingresos", response.content)

    def test_get_and_head_never_write(self):
        self.login(self.viewer)
        for params in ("", "?force=1", "?months=6", "?force=1&months=3"):
            for method in ("get", "head"):
                response = getattr(self.client, method)(reverse(self.url_name) + params)
                self.assertEqual(response.status_code, 200, (method, params))
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_download_content_is_computed_live(self):
        self.login(self.viewer)
        response = self.client.get(reverse(self.url_name))
        body = response.content.decode()
        self.assertIn("Total de Citas: 1", body)
        self.assertIn("Ingresos Totales: 15.00", body)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_months_parameter_is_validated(self):
        self.login(self.viewer)
        for bad in ("abc", "0", "-3", "25", "999999999", "1.5"):
            response = self.client.get(reverse(self.url_name), {"months": bad})
            self.assertEqual(response.status_code, 400, bad)
        response = self.client.get(reverse(self.url_name), {"months": "24"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().count("Mes: "), 24)
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_post_not_allowed(self):
        self.login(self.superuser)
        self.assertEqual(self.client.post(reverse(self.url_name)).status_code, 405)
        self.assertEqual(ReporteMensual.objects.count(), 0)


class ReportGenerationTests(AdminSecurityBase):
    url_name = "admin:reporte_personalizado"

    def test_get_does_not_write_and_hides_generate_form_without_permission(self):
        self.login(self.viewer)
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReporteMensual.objects.count(), 0)
        self.assertFalse(response.context["can_generate"])
        self.assertNotIn('name="months"', response.content.decode())

    def test_get_forbidden_without_view_permission(self):
        self.login(self.staff0)
        self.assertEqual(self.client.get(reverse(self.url_name)).status_code, 403)
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_post_without_csrf_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.superuser)
        response = client.post(reverse(self.url_name), {"months": "5"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_post_without_permission_is_rejected(self):
        for user in (self.staff0, self.viewer):
            self.login(user)
            response = self.client.post(reverse(self.url_name), {"months": "5"})
            self.assertEqual(response.status_code, 403, user.username)
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_post_requires_both_add_and_change(self):
        User = get_user_model()
        for codename in ("add_reportemensual", "change_reportemensual"):
            user = User.objects.create_user(f"only_{codename}", password=PASSWORD, is_staff=True)
            grant(user, "view_reportemensual", codename)
            self.login(user)
            self.assertEqual(self.client.post(reverse(self.url_name), {"months": "2"}).status_code, 403)
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_authorized_post_saves_reports_with_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.editor)
        page = client.get(reverse(self.url_name))
        self.assertTrue(page.context["can_generate"])
        token = client.cookies["csrftoken"].value
        response = client.post(reverse(self.url_name), {"months": "3", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReporteMensual.objects.count(), 3)
        current = ReporteMensual.objects.get(mes=timezone.localdate().replace(day=1))
        self.assertEqual(current.total_citas, 1)
        self.assertEqual(current.ingresos_totales, Decimal("15.00"))

    def test_default_is_five_months_and_idempotent(self):
        self.login(self.superuser)
        self.client.post(reverse(self.url_name))
        self.client.post(reverse(self.url_name))
        self.assertEqual(ReporteMensual.objects.count(), 5)

    def test_invalid_or_excessive_months_rejected_without_writes(self):
        self.login(self.superuser)
        for bad in ("abc", "0", "-1", "25", "99999999999999999999", "1.5"):
            response = self.client.post(reverse(self.url_name), {"months": bad})
            self.assertEqual(response.status_code, 400, bad)
        self.assertEqual(ReporteMensual.objects.count(), 0)

    def test_put_and_delete_methods_not_allowed(self):
        self.login(self.superuser)
        self.assertEqual(self.client.put(reverse(self.url_name)).status_code, 405)
        self.assertEqual(self.client.delete(reverse(self.url_name)).status_code, 405)


class ReportMensualAdminFormTests(AdminSecurityBase):
    def test_changelist_download_link_is_read_only_url(self):
        ReporteMensual.objects.create(mes=dt.date(2030, 1, 1))
        self.login(self.viewer)
        html = self.client.get(reverse("admin:reports_reportemensual_changelist")).content.decode()
        self.assertIn(reverse("admin:descargar_reporte"), html)
        self.assertNotIn("force=1", html)
