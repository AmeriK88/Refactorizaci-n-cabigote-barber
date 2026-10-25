import datetime as dt
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import connection
from django.template import engines
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from appointments.models import Cita
from appointments.services.admin_stats import count_appointments_by_month
from appointments.services.dashboard_stats import (
    appointment_day_summary,
    fecha_hora_mismatch,
    local_day_bounds,
    month_windows,
    monthly_appointment_counts,
    upcoming_appointments,
)
from core.context_processors import mensaje_especial_context
from core.models import ContadorVisitas, MensajeEspecial
from core.tests import STATIC_STORAGES
from products.models import Imagen
from services.models import Servicio

CANARY = ZoneInfo("Atlantic/Canary")
PASSWORD = "Dash-pass-12345"  # nosec - credencial de prueba


def local(y, m, d, hh=0, mm=0, ss=0):
    return dt.datetime(y, m, d, hh, mm, ss, tzinfo=CANARY)


def legacy_estimated_value(day):
    """Cálculo anterior (bucle Python) usado como referencia de equivalencia."""
    start, end = local_day_bounds(day)
    qs = Cita.objects.filter(fecha__gte=start, fecha__lt=end).select_related("producto", "servicio")
    total = Decimal("0")
    for c in qs:
        if c.servicio:
            total += c.servicio.precio or 0
        if c.producto and hasattr(c.producto, "precio"):
            total += c.producto.precio or 0
    return qs.count(), total


class StatsBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user("cliente", password=PASSWORD)
        cls.corte = Servicio.objects.create(nombre="Corte", descripcion="d", precio=Decimal("19.99"), duracion=30)
        cls.barba = Servicio.objects.create(nombre="Barba", descripcion="d", precio=Decimal("10.01"), duracion=20)
        cls.cera = Imagen.objects.create(titulo="Cera", imagen="p/a.jpg", precio=Decimal("12.34"))
        cls.sin_precio = Imagen.objects.create(titulo="Sin precio", imagen="p/b.jpg", precio=None)

    def cita(self, fecha, servicio=None, producto=None, hora=None):
        return Cita.objects.create(
            usuario=self.user,
            servicio=servicio or self.corte,
            producto=producto,
            fecha=fecha,
            hora=hora or timezone.localtime(fecha, CANARY).time(),
        )


@override_settings(TIME_ZONE="Atlantic/Canary")
class EstimatedValueTests(StatsBase):
    day = dt.date(2026, 3, 29)  # cambio de hora en Canarias: día de 23 horas

    def test_empty_day(self):
        count, value = appointment_day_summary(self.day)
        self.assertEqual((count, value), (0, Decimal("0.00")))
        self.assertIsInstance(value, Decimal)

    def test_equivalent_to_legacy_loop_with_optional_and_null_prices(self):
        d = self.day
        self.cita(local(2026, 3, 29, 9), self.corte)
        self.cita(local(2026, 3, 29, 10), self.barba, self.cera)
        self.cita(local(2026, 3, 29, 11), self.barba, self.sin_precio)  # producto con precio NULL
        self.cita(local(2026, 3, 29, 12), self.corte, self.cera)
        self.cita(local(2026, 3, 29, 12), self.corte, self.cera)  # mismo servicio y producto: no se deduplica
        count, value = appointment_day_summary(d)
        legacy_count, legacy_value = legacy_estimated_value(d)
        self.assertEqual(count, legacy_count)
        self.assertEqual(value, legacy_value)
        self.assertEqual(count, 5)
        self.assertEqual(value, Decimal("19.99") + Decimal("22.35") + Decimal("10.01") + Decimal("64.66"))

    def test_decimal_precision_is_exact(self):
        for _ in range(3):
            self.cita(local(2026, 3, 29, 9), self.corte, self.cera)
        _, value = appointment_day_summary(self.day)
        self.assertEqual(value, Decimal("96.99"))
        self.assertEqual(str(value), "96.99")

    def test_day_boundaries_use_canary_time_including_dst_day(self):
        start, end = local_day_bounds(self.day)
        self.assertEqual(end.astimezone(dt.timezone.utc) - start.astimezone(dt.timezone.utc), dt.timedelta(hours=23))
        self.cita(local(2026, 3, 28, 23, 59, 59))  # día anterior
        self.cita(local(2026, 3, 29, 0, 0, 0))     # incluida: inicio exacto
        self.cita(local(2026, 3, 29, 23, 59, 59))  # incluida: último segundo
        self.cita(local(2026, 3, 30, 0, 0, 0))     # día siguiente
        count, value = appointment_day_summary(self.day)
        self.assertEqual((count, value), (2, Decimal("39.98")))

    def test_summer_midnight_is_not_utc_midnight(self):
        self.cita(local(2026, 7, 10, 0, 30))   # 23:30 UTC del día 9: pertenece al día 10 local
        self.cita(local(2026, 7, 9, 23, 30))   # 22:30 UTC del día 9: pertenece al día 9 local
        self.assertEqual(appointment_day_summary(dt.date(2026, 7, 10))[0], 1)
        self.assertEqual(appointment_day_summary(dt.date(2026, 7, 9))[0], 1)

    def test_single_query_and_independent_of_rows(self):
        for i in range(25):
            self.cita(local(2026, 3, 29, 8, i), self.barba, self.cera)
        with CaptureQueriesContext(connection) as queries:
            appointment_day_summary(self.day)
        self.assertEqual(len(queries), 1)


@override_settings(TIME_ZONE="Atlantic/Canary")
class MonthlyStatsTests(StatsBase):
    def test_window_has_twelve_consecutive_months_across_year_change(self):
        windows = month_windows(12, now=local(2026, 2, 10, 12))
        labels = [w[0] for w in windows]
        self.assertEqual(labels, [
            "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08",
            "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02",
        ])
        for (_, _, end), (_, start, _) in zip(windows, windows[1:]):
            self.assertEqual(end, start)

    def test_window_for_january_goes_back_to_previous_february(self):
        labels = [w[0] for w in month_windows(12, now=local(2026, 1, 1, 0, 0))]
        self.assertEqual((labels[0], labels[-1]), ("2025-02", "2026-01"))

    def test_empty_database_returns_twelve_zero_months_without_placeholder(self):
        labels, counts = monthly_appointment_counts(12, now=local(2026, 6, 15))
        self.assertEqual(len(labels), 12)
        self.assertEqual(counts, [0] * 12)
        self.assertNotIn("No data", labels)

    def test_gaps_are_filled_and_counts_are_exact(self):
        now = local(2026, 2, 10, 12)
        self.cita(local(2025, 3, 1, 0, 0))     # primer instante de la ventana
        self.cita(local(2025, 2, 28, 23, 59, 59))  # fuera de la ventana
        self.cita(local(2025, 12, 31, 23, 59, 59))
        self.cita(local(2026, 1, 1, 0, 0, 0))
        self.cita(local(2026, 1, 1, 9))
        self.cita(local(2026, 2, 28, 18))      # futuro dentro del mes actual: cuenta
        self.cita(local(2026, 3, 1, 0, 0))     # mes futuro: fuera
        labels, counts = monthly_appointment_counts(12, now=now)
        result = dict(zip(labels, counts))
        self.assertEqual(result["2025-03"], 1)
        self.assertEqual(result["2025-12"], 1)
        self.assertEqual(result["2026-01"], 2)
        self.assertEqual(result["2026-02"], 1)
        self.assertEqual(sum(counts), 5)
        self.assertEqual(sum(1 for c in counts if c == 0), 8)
        self.assertNotIn("2025-02", result)
        self.assertNotIn("2026-03", result)

    def test_month_change_uses_local_time_not_utc(self):
        now = local(2026, 8, 20)
        self.cita(local(2026, 8, 1, 0, 30))   # 23:30 UTC de julio, pero agosto local
        self.cita(local(2026, 7, 31, 23, 30))  # julio local
        result = dict(zip(*monthly_appointment_counts(3, now=now)))
        self.assertEqual(result, {"2026-06": 0, "2026-07": 1, "2026-08": 1})

    def test_single_query(self):
        self.cita(local(2026, 1, 5))
        with CaptureQueriesContext(connection) as queries:
            monthly_appointment_counts(12, now=local(2026, 2, 1))
        self.assertEqual(len(queries), 1)

    def test_invalid_months(self):
        with self.assertRaises(ValueError):
            monthly_appointment_counts(0)

    def test_legacy_wrapper_keeps_signature_and_png_still_renders(self):
        labels, counts = count_appointments_by_month(months_back=12)
        self.assertEqual(len(labels), len(counts), 12)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class ChartEndpointAndQueryTests(StatsBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.superuser = User.objects.create_superuser("root", "r@example.com", PASSWORD)
        cls.staff0 = User.objects.create_user("staff0", password=PASSWORD, is_staff=True)
        cls.viewer = User.objects.create_user("viewer", password=PASSWORD, is_staff=True)
        cls.viewer.user_permissions.add(Permission.objects.get(codename="view_cita"))

    def get_json(self, user):
        self.client.force_login(user)
        return self.client.get(reverse("admin:cita_graph_data"))

    def test_json_shape_for_chartjs_with_empty_database(self):
        response = self.get_json(self.superuser)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(data), {"labels", "counts"})
        self.assertEqual(len(data["labels"]), 12)
        self.assertEqual(data["counts"], [0] * 12)
        self.assertNotIn("No data", data["labels"])
        self.assertEqual(data["labels"][-1], timezone.localdate().strftime("%Y-%m"))

    def test_json_counts_current_month(self):
        self.cita(timezone.now())
        data = self.get_json(self.viewer).json()
        self.assertEqual(data["counts"][-1], 1)

    def test_json_permission_still_enforced(self):
        response = self.get_json(self.staff0)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(b"counts", response.content)

    def test_chart_endpoint_query_budget(self):
        self.client.force_login(self.superuser)
        self.client.get(reverse("admin:cita_graph_data"))
        with CaptureQueriesContext(connection) as queries:
            self.client.get(reverse("admin:cita_graph_data"))
        self.assertLessEqual(len(queries), 3)  # sesión + usuario + 1 agregación

    def test_dashboard_page_has_no_site_queries_from_context_processor(self):
        self.client.force_login(self.superuser)
        self.client.get(reverse("admin:cita_dashboard"))
        with CaptureQueriesContext(connection) as queries:
            self.client.get(reverse("admin:cita_dashboard"))
        sql = " ".join(q["sql"] for q in queries)
        for table in ("core_mensajeespecial", "core_contadorvisitas"):
            self.assertNotIn(table, sql)

    def home_queries(self, user):
        self.client.force_login(user)
        self.client.get("/en/admin/")  # calienta cachés (tema, content types)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/en/admin/")
        self.assertEqual(response.status_code, 200)
        return queries

    def test_dashboard_query_budget_does_not_scale_with_rows(self):
        few = len(self.home_queries(self.superuser))
        for i in range(30):
            self.cita(timezone.now(), self.barba, self.cera)
        many = len(self.home_queries(self.superuser))
        self.assertEqual(few, many)
        self.assertLessEqual(many, 9)  # sesión, usuario, resumen+próximas citas, servicios, usuarios (+margen)

    def test_dashboard_has_no_duplicate_or_unused_queries(self):
        queries = self.home_queries(self.superuser)
        sqls = [q["sql"] for q in queries]
        self.assertEqual(len(sqls), len(set(sqls)))
        joined = " ".join(sqls)
        self.assertNotIn("`is_active` = 1", joined)
        self.assertNotIn("core_mensajeespecial", joined)
        self.assertEqual(sum("appointments_cita" in s for s in sqls), 2)  # resumen + próximas citas

    def test_restricted_user_still_runs_no_restricted_queries(self):
        queries = self.home_queries(self.staff0)
        joined = " ".join(q["sql"] for q in queries)
        for table in ("appointments_cita", "services_servicio"):
            self.assertNotIn(table, joined)

    def test_dashboard_label_is_not_presented_as_cash_income(self):
        self.client.force_login(self.superuser)
        html = self.client.get("/en/admin/").content.decode()
        self.assertIn("Valor estimado de reservas", html)
        self.assertNotIn("Ingresos hoy", html)

    def test_dashboard_value_matches_legacy_calculation(self):
        now = timezone.now()
        self.cita(now, self.corte, self.cera)
        self.cita(now, self.barba, self.sin_precio)
        self.client.force_login(self.superuser)
        response = self.client.get("/en/admin/")
        expected_count, expected_value = legacy_estimated_value(timezone.localdate())
        self.assertEqual(response.context["citas_hoy"], expected_count)
        self.assertEqual(response.context["valor_estimado_hoy"], expected_value)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class SiteContextProcessorTests(TestCase):
    def render(self, source):
        request = RequestFactory().get("/")
        return engines["django"].from_string(source).render({}, request)

    def test_values_are_lazy_and_not_queried_until_used(self):
        request = RequestFactory().get("/")
        with CaptureQueriesContext(connection) as queries:
            context = mensaje_especial_context(request)
        self.assertEqual(len(queries), 0)
        self.assertIn("APP_VERSION", context)

    def test_templates_unused_values_cost_nothing(self):
        with CaptureQueriesContext(connection) as queries:
            self.render("sin variables")
        self.assertEqual(len(queries), 0)

    def test_public_values_are_unchanged_when_used(self):
        get_user_model().objects.create_user("a", password=PASSWORD)
        get_user_model().objects.create_user("b", password=PASSWORD, is_active=False)
        ContadorVisitas.objects.create(pk=1, total=7)
        today = timezone.now().date()
        MensajeEspecial.objects.create(
            titulo="Aviso", contenido="x", activo=True,
            fecha_inicio=today - dt.timedelta(days=1), fecha_fin=today + dt.timedelta(days=1),
        )
        out = self.render("{{ total_usuarios|default:'0' }}|{{ contador_global }}|{% if special_message %}{{ special_message.titulo }}{% endif %}")
        self.assertEqual(out, "1|7|Aviso")

    def test_defaults_when_empty(self):
        out = self.render("{{ contador_global }}|{% if special_message %}si{% else %}no{% endif %}")
        self.assertEqual(out, "0|no")

    def test_each_value_is_queried_at_most_once_per_render(self):
        ContadorVisitas.objects.create(pk=1, total=3)
        with CaptureQueriesContext(connection) as queries:
            self.render("{{ contador_global }}{{ contador_global }}{{ contador_global }}")
        self.assertEqual(len(queries), 1)


@override_settings(TIME_ZONE="Atlantic/Canary")
class UpcomingAppointmentsTests(StatsBase):
    now = local(2026, 5, 10, 12)

    def test_orders_by_fecha_and_ignores_hora(self):
        # `hora` contradictoria a propósito: la fuente de verdad es `fecha`
        late = self.cita(local(2026, 5, 10, 18), hora=dt.time(6, 0))
        early = self.cita(local(2026, 5, 10, 13), hora=dt.time(23, 0))
        tomorrow = self.cita(local(2026, 5, 11, 9), hora=dt.time(1, 0))
        result = upcoming_appointments(now=self.now)
        self.assertEqual([c.pk for c in result], [early.pk, late.pk, tomorrow.pk])

    def test_excludes_past_and_includes_exact_now(self):
        self.cita(local(2026, 5, 10, 11, 59))
        exact = self.cita(local(2026, 5, 10, 12, 0))
        self.assertEqual([c.pk for c in upcoming_appointments(now=self.now)], [exact.pk])

    def test_limit_and_stable_tiebreak(self):
        ids = [self.cita(local(2026, 5, 11, 9)).pk for _ in range(4)]
        result = upcoming_appointments(limit=3, now=self.now)
        self.assertEqual([c.pk for c in result], ids[:3])

    def test_single_query_without_n_plus_one(self):
        for i in range(5):
            self.cita(local(2026, 5, 11, 9 + i), producto=self.cera)
        with CaptureQueriesContext(connection) as queries:
            result = upcoming_appointments(now=self.now)
            names = [(c.usuario.username, c.servicio.nombre, c.producto.titulo) for c in result]
        self.assertEqual(len(queries), 1)
        self.assertEqual(len(names), 5)

    def test_mismatch_detection(self):
        ok = self.cita(local(2026, 5, 11, 9, 30))
        bad = self.cita(local(2026, 5, 11, 0, 0), hora=dt.time(6, 0))  # caso visto al editar desde el admin
        self.assertFalse(fecha_hora_mismatch(ok))
        self.assertTrue(fecha_hora_mismatch(bad))
