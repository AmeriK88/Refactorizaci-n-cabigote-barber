import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse

from core.test_admin_security import AdminSecurityBase, PASSWORD
from core.tests import STATIC_STORAGES

NEW_PASSWORD = "Nuev0-Secreto-9731"  # nosec - credencial de prueba
CSS = "admin/css/adminDashboard.css"
JS = "admin/js/admin-theme.js"
PROJECT_TEMPLATES = Path(settings.BASE_DIR) / "templates" / "registration"


def template_origins(response):
    return [str(t.origin.name) for t in response.templates if t.origin and t.origin.name]


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False, AXES_ENABLED=False)
class PasswordResetFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("ana", "ana@example.com", PASSWORD)

    def assert_branded(self, response):
        html = response.content.decode()
        head = html.split("</head>", 1)[0]
        self.assertEqual(head.count(CSS), 1, "la hoja debe cargarse una vez, en <head>")
        self.assertEqual(html.count(CSS), 1)
        self.assertEqual(html.count(JS), 1)
        self.assertEqual(html.count('id="cb-admin-theme"'), 1)
        self.assertRegex(html, r'<body class="[^"]*\bcb-auth\b')
        self.assertIn('class="cb-auth-card', html)
        return html

    def reset_link(self):
        match = re.search(r"https?://[^/\s]+(/[^\s]+/reset/[^\s]+)", mail.outbox[-1].body)
        self.assertIsNotNone(match, mail.outbox[-1].body)
        return match.group(1)

    def test_routes_resolve_to_django_auth_views(self):
        expected = {
            "/es/accounts/password_reset/": PasswordResetView,
            "/es/accounts/password_reset/done/": PasswordResetDoneView,
            "/es/accounts/reset/MQ/set-password/": PasswordResetConfirmView,
            "/es/accounts/reset/done/": PasswordResetCompleteView,
        }
        for path, view in expected.items():
            with self.subTest(path=path):
                self.assertIs(resolve(path).func.view_class, view)

    def test_each_page_uses_project_template_and_loads_shared_assets(self):
        pages = {
            "/es/accounts/password_reset/": "password_reset_form.html",
            "/es/accounts/password_reset/done/": "password_reset_done.html",
            "/es/accounts/reset/MQ/invalid-token/": "password_reset_confirm.html",
            "/es/accounts/reset/done/": "password_reset_complete.html",
        }
        for path, name in pages.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                origins = template_origins(response)
                self.assertIn(str(PROJECT_TEMPLATES / name), origins)
                self.assertTrue(any("django" in o and name in o for o in origins), origins)
                self.assert_branded(response)

    def test_form_has_csrf_and_accessible_email_field(self):
        html = self.assert_branded(self.client.get("/es/accounts/password_reset/"))
        self.assertIn("csrfmiddlewaretoken", html)
        self.assertRegex(html, r'<label for="id_email">')
        self.assertIn('id="id_email"', html)

    def test_post_without_csrf_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/es/accounts/password_reset/", {"email": "ana@example.com"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(mail.outbox, [])

    def test_known_and_unknown_emails_are_indistinguishable(self):
        known = self.client.post("/es/accounts/password_reset/", {"email": "ana@example.com"})
        unknown = self.client.post("/es/accounts/password_reset/", {"email": "nadie@example.com"})
        self.assertEqual((known.status_code, known.url), (unknown.status_code, unknown.url))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])
        done_known = self.client.get(known.url).content
        done_unknown = self.client.get(unknown.url).content
        self.assertEqual(re.sub(rb"csrf\S+", b"", done_known), re.sub(rb"csrf\S+", b"", done_unknown))
        self.assertNotIn(b"nadie@example.com", done_unknown)

    def test_invalid_email_shows_error_without_sending(self):
        response = self.client.post("/es/accounts/password_reset/", {"email": "no-es-un-email"})
        self.assertEqual(response.status_code, 200)
        html = self.assert_branded(response)
        self.assertIn("errorlist", html)
        self.assertEqual(mail.outbox, [])

    def test_full_reset_flow_changes_password_and_link_is_single_use(self):
        self.client.post("/es/accounts/password_reset/", {"email": "ana@example.com"})
        link = self.reset_link()

        redirect = self.client.get(link)
        self.assertEqual(redirect.status_code, 302)
        form_url = redirect.url
        page = self.client.get(form_url)
        self.assertEqual(page.status_code, 200)
        html = self.assert_branded(page)
        self.assertIn("csrfmiddlewaretoken", html)
        self.assertIn('id="id_new_password1"', html)

        weak = self.client.post(form_url, {"new_password1": "123", "new_password2": "123"})
        self.assertEqual(weak.status_code, 200)
        self.assertIn("errorlist", self.assert_branded(weak))
        mismatch = self.client.post(form_url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD + "x"})
        self.assertEqual(mismatch.status_code, 200)
        self.assertIn("errorlist", mismatch.content.decode())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

        done = self.client.post(form_url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})
        self.assertRedirects(done, "/es/accounts/reset/done/", fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assert_branded(self.client.get(done.url))

        reused = Client().get(link, follow=True)
        html = reused.content.decode()
        self.assertEqual(reused.status_code, 200)
        self.assertFalse(reused.context["validlink"])
        self.assertNotIn("id_new_password1", html)
        self.assertIn(CSS, html)

    def test_forged_token_is_invalid(self):
        response = self.client.get("/es/accounts/reset/MQ/abc-0123456789abcdef/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["validlink"])
        self.assertNotIn("<form", response.content.decode().split('id="content-main"', 1)[1])


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False, AXES_ENABLED=False)
class PasswordResetInvalidLinkAndEmailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("ana", "ana@example.com", PASSWORD)

    def request_link(self):
        self.client.post("/es/accounts/password_reset/", {"email": "ana@example.com"})
        match = re.search(r"https?://[^/\s]+(/[^\s]+/reset/[^\s]+)", mail.outbox[-1].body)
        self.assertIsNotNone(match)
        return match.group(1)

    def assert_invalid_page(self, response):
        html = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["validlink"])
        head = html.split("</head>", 1)[0]
        self.assertEqual(head.count(CSS), 1)
        self.assertEqual(html.count(CSS), 1)
        self.assertEqual(html.count(JS), 1)
        self.assertEqual(html.count('id="cb-admin-theme"'), 1)
        self.assertIn("Enlace de recuperación no válido", html)
        self.assertIn("cb-auth-card--invalid", html)
        self.assertIn(f'href="{reverse("password_reset")}"', html)
        self.assertIn("Solicitar un nuevo enlace", html)
        self.assertNotIn("<form", html.split('id="content-main"', 1)[1])
        self.assertNotIn("ana@example.com", html)
        return html

    def test_forged_link_renders_branded_invalid_state(self):
        self.assert_invalid_page(self.client.get("/es/accounts/reset/MQ/abc-0123456789abcdef/", follow=True))

    def test_reused_link_renders_branded_invalid_state(self):
        link = self.request_link()
        form_url = self.client.get(link).url
        self.client.post(form_url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})
        self.assert_invalid_page(Client().get(link, follow=True))

    @override_settings(PASSWORD_RESET_TIMEOUT=-1)
    def test_expired_link_renders_branded_invalid_state(self):
        link = self.request_link()
        self.assert_invalid_page(self.client.get(link, follow=True))

    def test_invalid_state_title_and_request_new_link_flow(self):
        response = self.client.get("/es/accounts/reset/MQ/abc-0123456789abcdef/", follow=True)
        self.assertIn("Enlace de recuperación no válido", response.content.decode().split("</title>")[0])
        again = self.client.get(reverse("password_reset"))
        self.assertEqual(again.status_code, 200)

    def test_valid_link_shows_validator_help_and_error_states(self):
        link = self.request_link()
        form_url = self.client.get(link).url
        page = self.client.get(form_url)
        html = page.content.decode()
        self.assertTrue(page.context["validlink"])
        self.assertEqual(html.count(CSS), 1)
        self.assertEqual(html.count('id="cb-admin-theme"'), 1)
        self.assertIn('id="id_new_password1_helptext"', html)
        self.assertIn("8", html.split("id_new_password1_helptext", 1)[1][:600])
        self.assertIn('type="submit"', html)
        bad = self.client.post(form_url, {"new_password1": "12345678", "new_password2": "12345678"})
        self.assertEqual(bad.status_code, 200)
        self.assertIn("errorlist", bad.content.decode())
        self.assertIn("errornote", bad.content.decode())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_valid_link_post_without_csrf_is_rejected(self):
        link = self.request_link()
        form_url = self.client.get(link).url
        strict = Client(enforce_csrf_checks=True)
        strict.cookies = self.client.cookies
        response = strict.post(form_url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})
        self.assertEqual(response.status_code, 403)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_email_has_cabigote_identity_correct_url_and_no_sensitive_data(self):
        link = self.request_link()
        message = mail.outbox[-1]
        site = Site.objects.get_current()
        self.assertIn("Ca'Bigote", message.subject)
        self.assertNotIn("Django", message.subject + message.body)
        self.assertEqual(message.to, ["ana@example.com"])
        self.assertIn(f"://{site.domain}{link}", message.body)
        self.assertIn("ignorar", message.body)
        self.assertNotIn("ana@example.com", message.body)
        self.assertNotIn("Hola, ana", message.body)
        html_body, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertEqual(html_body.count(f"://{site.domain}{link}"), 3)  # botón, enlace y texto visible
        self.assertIn("Ca'Bigote", html_body)
        self.assertNotIn("<script", html_body)

    def test_email_link_works_end_to_end(self):
        link = self.request_link()
        self.assertEqual(self.client.get(link).status_code, 302)

    def test_url_names_and_allauth_flow_are_preserved(self):
        self.assertEqual(reverse("password_reset"), "/es/accounts/password_reset/")
        self.assertEqual(resolve("/es/accounts/password_reset/").url_name, "password_reset")
        self.assertEqual(resolve("/es/accounts/password/reset/").url_name, "account_reset_password")
        self.assertEqual(self.client.get("/es/accounts/password/reset/").status_code, 200)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class PasswordChangeStillBrandedTests(AdminSecurityBase):
    def test_admin_password_change_pages_load_shared_assets(self):
        self.login(self.staff0)
        for name in ("admin:password_change", "admin:password_change_done"):
            with self.subTest(name=name):
                html = self.client.get(reverse(name)).content.decode()
                self.assertIn(CSS, html)
                self.assertIn(JS, html)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class AppointmentChartPagesTests(AdminSecurityBase):
    names = ("admin:cita_dashboard", "admin:cita_graph")

    def test_templates_have_no_inline_styles_or_literal_colors(self):
        base = Path(settings.BASE_DIR) / "appointments" / "templates" / "admin"
        for name in ("dashboard_citas.html", "grafico_citas.html"):
            source = (base / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertNotIn("style=", source)
                self.assertNotIn("<style", source)
                self.assertNotRegex(source, r"#[0-9a-fA-F]{3,6}\b")

    def test_authorized_user_gets_branded_shell_and_single_h1(self):
        self.login(self.viewer)
        for name in self.names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertIn(CSS, html)
                self.assertIn(JS, html)
                self.assertIn('id="cb-admin-theme"', html)
                self.assertIn('id="user-tools"', html)
                content = html.split('id="content-start"', 1)[1]
                self.assertEqual(len(re.findall(r"<h1[\s>]", content)), 1)

    def test_chart_urls_and_data_endpoint_are_preserved(self):
        self.login(self.viewer)
        html = self.client.get(reverse("admin:cita_dashboard")).content.decode()
        self.assertIn(reverse("admin:cita_graph_data"), html)
        self.assertIn("citas_dashboard_chart.js", html)
        self.assertIn('id="chart-citas"', html)
        self.assertIn("data:image/png;base64", self.client.get(reverse("admin:cita_graph")).content.decode())

    def test_access_control_is_preserved(self):
        for name in self.names:
            with self.subTest(name=name):
                self.assertEqual(Client().get(reverse(name)).status_code, 302)
                self.assertEqual(self.login(self.plain, Client()).get(reverse(name)).status_code, 302)
                self.assertEqual(self.login(self.staff0, Client()).get(reverse(name)).status_code, 403)
                self.assertEqual(self.login(self.superuser, Client()).get(reverse(name)).status_code, 200)
