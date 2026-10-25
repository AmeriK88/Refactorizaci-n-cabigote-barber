import datetime as dt
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from appointments.models import Cita
from appointments.services.dashboard_stats import dashboard_appointment_summary
from core.test_admin_security import AdminSecurityBase, grant
from services.models import Servicio

CSS = Path(__file__).resolve().parents[1] / "static" / "admin" / "css" / "adminDashboard.css"
EMOJIS = "📆💶🛠👥📥👁🔮✂🧠📅📊"


class DashboardBase(AdminSecurityBase):
    url = "/en/admin/"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.lucia = User.objects.create_user(
            "lucia_cliente", "lucia@example.com", "x-Pass-12345", first_name="Lucía", last_name="Pérez"
        )
        cls.barba = Servicio.objects.create(
            nombre="Barba premium", descripcion="d", precio="12.00", duracion=30
        )

    def future(self, days=1, hours=0, **kwargs):
        moment = timezone.now() + dt.timedelta(days=days, hours=hours)
        values = {
            "usuario": self.lucia,
            "servicio": self.barba,
            "fecha": moment,
            "hora": timezone.localtime(moment).time(),
        }
        values.update(kwargs)
        return Cita.objects.create(**values)

    def html(self, user):
        self.login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def content(self, user):
        return self.html(user).split('id="content-main"', 1)[1]


class DuplicateNavigationTests(DashboardBase):
    def test_central_app_list_is_gone_but_sidebar_remains(self):
        html = self.html(self.superuser)
        self.assertNotIn("cb-admin-app-list", html)
        self.assertNotIn("No tienes permisos para ver ninguna aplicación", html)
        # admin/app_list.html solo se pinta ahora en la barra lateral
        self.assertEqual(html.count("app-auth module"), 1)
        self.assertEqual(html.count("app-appointments module"), 1)
        self.assertEqual(html.count('id="nav-sidebar"'), 1)
        self.assertIn(f'href="{reverse("admin:appointments_cita_changelist")}"', html)

    def test_mobile_navigation_hooks_are_present(self):
        html = self.html(self.viewer)
        self.assertEqual(html.count('id="toggle-nav-sidebar"'), 1)
        self.assertEqual(html.count("admin/js/admin-nav.js"), 1)
        self.assertEqual(html.count("admin/js/admin-theme.js"), 1)
        self.assertIn('id="cb-admin-theme"', html)

    def test_sidebar_respects_permissions_and_hint_explains_navigation(self):
        self.assertIn("menú lateral", self.html(self.viewer))
        staff_html = self.html(self.staff0)
        self.assertNotIn(f'href="{reverse("admin:appointments_cita_changelist")}"', staff_html)
        self.assertIn("no tiene apartados asignados", staff_html)

    def test_native_context_still_provides_app_list(self):
        self.login(self.superuser)
        response = self.client.get(self.url)
        self.assertTrue(response.context["app_list"])
        self.assertTrue(response.context["available_apps"])

    def test_title_user_name_and_date(self):
        html = self.html(self.viewer)
        self.assertEqual(html.count('id="cb-dash-title"'), 1)
        self.assertIn("Hola,", html)
        self.assertIn("<span>viewer</span>", html)
        self.assertIn(str(timezone.localdate().year), self.content(self.viewer))

    def test_no_emoji_icons_in_dashboard(self):
        content = self.content(self.superuser)
        for emoji in EMOJIS:
            self.assertNotIn(emoji, content)
        self.assertIn('aria-hidden="true"', content)


class DashboardPermissionTests(DashboardBase):
    def test_staff_without_permissions_sees_only_welcome(self):
        html = self.html(self.staff0)
        for text in ("Resumen operativo", "Próximas citas", "Accesos rápidos</h2>", "cb-dash-kpi", "cb-dash-appointment"):
            self.assertNotIn(text, html)
        self.assertIn("cb-dash-hero", html)

    def test_cita_permission_unlocks_summary_and_upcoming_only(self):
        User = get_user_model()
        user = User.objects.create_user("only_cita", "oc@example.com", "x-Pass-12345", is_staff=True)
        grant(user, "view_cita")
        self.future()
        content = self.content(user)
        self.assertIn("Próximas citas", content)
        self.assertIn("Valor estimado de reservas", content)
        self.assertNotIn("Servicios en catálogo", content)
        self.assertNotIn("Usuarios registrados", content)
        self.assertNotIn(reverse("admin:auth_user_changelist"), content)

    def test_user_permission_alone_exposes_no_appointment_data(self):
        User = get_user_model()
        user = User.objects.create_user("only_user", "ou@example.com", "x-Pass-12345", is_staff=True)
        grant(user, "view_user")
        self.future()
        html = self.html(user)
        self.assertIn("Usuarios registrados", html)
        for text in ("Próximas citas", "Lucía", "lucia_cliente", "Barba premium", "Valor estimado", "Sin revisar"):
            self.assertNotIn(text, html)

    def test_restricted_user_context_has_no_appointment_data(self):
        self.login(self.staff0)
        ctx = self.client.get(self.url).context
        self.assertEqual(ctx["proximas_citas"], [])
        self.assertIsNone(ctx["citas_sin_ver"])

    def test_restricted_user_runs_no_appointment_query(self):
        self.future()
        self.login(self.staff0)
        with CaptureQueriesContext(connection) as queries:
            self.client.get(self.url)
        self.assertNotIn("appointments_cita", " ".join(q["sql"] for q in queries))

    def test_superuser_sees_all_sections(self):
        self.future()
        html = self.html(self.superuser)
        for text in ("Resumen operativo", "Próximas citas", "Accesos rápidos", "Servicios en catálogo", "Usuarios registrados"):
            self.assertIn(text, html)

    def test_quick_actions_match_permissions(self):
        content = self.content(self.editor)  # solo informes
        self.assertIn(reverse("admin:descargar_reporte"), content)
        self.assertNotIn(reverse("admin:appointments_cita_changelist_hoy"), content)
        self.assertNotIn("Próximas citas", content)


class UpcomingAppointmentsSectionTests(DashboardBase):
    def test_lists_future_appointments_ordered_by_date_and_limited(self):
        created = [self.future(days=d) for d in (6, 2, 5, 1, 4, 3, 7)]
        self.login(self.viewer)
        response = self.client.get(self.url)
        listed = response.context["proximas_citas"]
        by_date = sorted(created, key=lambda c: (c.fecha, c.pk))
        self.assertEqual([c.pk for c in listed], [c.pk for c in by_date[:5]])
        html = response.content.decode()
        positions = [html.index(reverse("admin:appointments_cita_change", args=[c.pk])) for c in by_date[:5]]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn(reverse("admin:appointments_cita_change", args=[by_date[5].pk]), html)

    def test_past_appointments_are_excluded(self):
        past = self.future(days=-2)
        html = self.html(self.viewer)
        self.assertNotIn(reverse("admin:appointments_cita_change", args=[past.pk]), html)
        self.assertIn("No hay citas próximas", html)

    def test_empty_state_has_useful_message_and_link(self):
        Cita.objects.all().delete()
        html = self.html(self.viewer)
        self.assertIn("No hay citas próximas", html)
        self.assertIn(f'{reverse("admin:appointments_cita_changelist")}?year=all', html)

    def test_row_shows_client_service_and_review_badge(self):
        seen = self.future(days=1, vista=True)
        unseen = self.future(days=2)
        html = self.html(self.viewer)
        self.assertIn("Lucía Pérez", html)
        self.assertIn("Barba premium", html)
        self.assertEqual(html.count("Sin revisar</span>"), 1)
        self.assertIn(reverse("admin:appointments_cita_change", args=[seen.pk]), html)
        self.assertIn(reverse("admin:appointments_cita_change", args=[unseen.pk]), html)

    def test_row_links_are_reachable_for_viewers(self):
        cita = self.future()
        self.login(self.viewer)
        self.assertEqual(self.client.get(reverse("admin:appointments_cita_change", args=[cita.pk])).status_code, 200)

    def test_time_uses_fecha_in_local_timezone(self):
        cita = self.future(hora=dt.time(3, 33))  # `hora` contradictoria: no debe usarse
        local = timezone.localtime(cita.fecha)
        html = self.html(self.viewer)
        self.assertIn(f'datetime="{local.isoformat()}"', html)
        self.assertNotIn("03:33", html)

    def test_no_n_plus_one(self):
        self.login(self.viewer)
        self.future()
        self.client.get(self.url)
        with CaptureQueriesContext(connection) as one:
            self.client.get(self.url)
        for d in range(2, 8):
            self.future(days=d, usuario=self.client_user)
        with CaptureQueriesContext(connection) as many:
            self.client.get(self.url)
        self.assertEqual(len(one), len(many))

    def test_query_budget_for_superuser(self):
        self.login(self.superuser)
        self.future()
        self.client.get(self.url)
        with CaptureQueriesContext(connection) as queries:
            self.client.get(self.url)
        self.assertLessEqual(len(queries), 9)
        sqls = [q["sql"] for q in queries]
        self.assertEqual(len(sqls), len(set(sqls)))
        self.assertEqual(sum("appointments_cita" in s for s in sqls), 2)


class PendingReviewTests(DashboardBase):
    def test_counts_only_future_unseen_appointments(self):
        Cita.objects.all().delete()
        self.future(days=1)
        self.future(days=2)
        self.future(days=3, vista=True)
        self.future(days=-3)
        self.assertEqual(dashboard_appointment_summary()["pending_review"], 2)
        self.login(self.viewer)
        self.assertEqual(self.client.get(self.url).context["citas_sin_ver"], 2)

    def test_summary_keeps_today_count_and_value(self):
        Cita.objects.all().delete()
        now = timezone.now()
        self.future(fecha=now + dt.timedelta(seconds=30))
        summary = dashboard_appointment_summary(now=now)
        self.assertEqual(summary["today"], 1)
        self.assertEqual(str(summary["estimated_value"]), "12.00")

    def test_summary_is_empty_on_empty_database(self):
        Cita.objects.all().delete()
        self.assertEqual(
            dashboard_appointment_summary(),
            {"today": 0, "estimated_value": 0, "pending_review": 0},
        )

    def test_summary_is_single_query(self):
        with CaptureQueriesContext(connection) as queries:
            dashboard_appointment_summary()
        self.assertEqual(len(queries), 1)


class DashboardCssTests(DashboardBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        css = CSS.read_text(encoding="utf-8")
        cls.block = css[css.index("PORTADA DEL ADMINISTRADOR (fase 3D.4)"):]

    def test_new_block_uses_tokens_only(self):
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,8}\b", self.block))
        self.assertNotIn("!important", self.block)

    def test_reduced_motion_and_focus_states_are_covered(self):
        self.assertIn("prefers-reduced-motion: reduce", self.block)
        self.assertIn(":focus-visible", self.block)
        self.assertIn("var(--cb-ring)", self.block)

    def test_every_class_used_by_the_template_is_styled(self):
        self.future()
        content = self.content(self.superuser)
        used = {
            name
            for value in re.findall(r'class="([^"]*)"', content)
            for name in value.split()
            if name.startswith("cb-dash")
        }
        self.assertTrue(used)
        for name in used:
            self.assertIn(f".{name}", self.block, name)
