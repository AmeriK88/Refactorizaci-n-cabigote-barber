from pathlib import Path

import admin_interface
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse


class AdminThemeIntegrationTests(SimpleTestCase):
    def test_theme_assets_and_both_controls_are_in_shared_partial(self):
        storages = {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
        with override_settings(STORAGES=storages):
            rendered = get_template("admin/color_theme_toggle.html").render({})

        self.assertEqual(rendered.count("admin/css/adminDashboard.css"), 1)
        self.assertEqual(rendered.count("admin/js/admin-theme.js"), 1)
        self.assertEqual(rendered.count('id="cb-admin-theme"'), 1)
        self.assertEqual(rendered.count('class="theme-toggle"'), 1)
        self.assertIn('<option value="light">Claro</option>', rendered)
        self.assertIn('<option value="dark">Oscuro</option>', rendered)
        self.assertIn('<option value="auto">Sistema</option>', rendered)

    def test_django_admin_interface_base_site_remains_in_use(self):
        base_site = get_template("admin/base_site.html")
        base = get_template("admin/base.html")
        stylesheet = (
            Path(__file__).resolve().parents[1]
            / "static"
            / "admin"
            / "css"
            / "adminDashboard.css"
        )
        css_source = stylesheet.read_text(encoding="utf-8")

        # El proyecto solo añade una extensión recursiva fina; la plantilla del paquete sigue en la cadena.
        self.assertNotIn("admin_interface", base_site.origin.name)
        self.assertIn('{% extends "admin/base_site.html" %}', base_site.template.source)
        self.assertLess(len(base_site.template.source.splitlines()), 15)
        self.assertEqual(base_site.template.source.count("<link"), 1)
        self.assertIn("{{ block.super }}", base_site.template.source)
        self.assertEqual(
            base.template.source.count('{% include "admin/color_theme_toggle.html" %}'),
            1,
        )
        self.assertIn("html:root body.admin-interface {", css_source)

    def test_login_uses_a_small_wrapper_over_the_native_login_template(self):
        self.assertEqual(admin.site.login_template, "admin/cabigote_login.html")

        login_wrapper = get_template("admin/cabigote_login.html")
        self.assertIn('{% extends "admin/login.html" %}', login_wrapper.template.source)
        self.assertIn('{% include "admin/color_theme_toggle.html" %}', login_wrapper.template.source)

    def test_registered_admins_do_not_add_duplicate_theme_css(self):
        for model_admin in admin.site._registry.values():
            with self.subTest(model=model_admin.model._meta.label):
                css = model_admin.media._css.get("all", ())
                self.assertNotIn("admin/css/adminDashboard.css", css)


class AdminShellStylesheetTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        path = Path(__file__).resolve().parents[1] / "static" / "admin" / "css" / "adminDashboard.css"
        cls.css = path.read_text(encoding="utf-8")

    def test_shell_components_use_stable_native_selectors(self):
        for selector in (
            "body.admin-interface #header",
            "body.admin-interface #header #user-tools",
            "body.admin-interface div.breadcrumbs",
            "body.admin-interface #nav-sidebar",
            "body.admin-interface #nav-sidebar .current-model",
            "body.admin-interface #content",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, self.css)

    def test_shell_uses_tokens_and_does_not_reload_assets(self):
        shell = self.css.split("SHELL ADMINISTRATIVO", 1)[1]
        self.assertNotRegex(shell, r"#[0-9a-fA-F]{3,6}\b")
        self.assertNotIn("@import", self.css)
        self.assertIn("prefers-reduced-motion", shell)
        self.assertIn(":focus-visible", shell)

    def test_dark_header_tokens_exist_in_explicit_and_system_dark_modes(self):
        self.assertEqual(self.css.count("--cb-header-bg: #0f0e0d;"), 2)

    def test_popups_do_not_receive_the_global_partial(self):
        base = get_template("admin/base.html").template.source
        header = base.index("<header")
        include = base.index('{% include "admin/color_theme_toggle.html" %}')
        popup_guard = base.rfind("{% if not is_popup %}", 0, include)
        self.assertGreater(popup_guard, base.rfind("<body", 0, header))


STATIC_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class AdminRenderedPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.superuser = user_model.objects.create_superuser(
            username="root", email="root@example.com", password="pw-12345-Test"
        )
        cls.staff_without_perms = user_model.objects.create_user(
            username="staff", email="staff@example.com", password="pw-12345-Test", is_staff=True
        )

    def get(self, user, url):
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_normal_pages_load_shared_assets_exactly_once(self):
        html = self.get(self.superuser, reverse("admin:auth_group_add"))
        self.assertEqual(html.count("admin/css/adminDashboard.css"), 1)
        self.assertEqual(html.count("admin/js/admin-theme.js"), 1)
        self.assertEqual(html.count("admin/js/admin-nav.js"), 1)
        self.assertEqual(html.count('id="cb-admin-theme"'), 1)
        self.assertIn("admin_interface/css/admin-interface.css", html)

    def test_popups_load_the_stylesheet_once_without_shell_scripts(self):
        for url in (
            reverse("admin:auth_group_add") + "?_popup=1",
            reverse("admin:auth_user_changelist") + "?_popup=1&_to_field=id",
        ):
            with self.subTest(url=url):
                html = self.get(self.superuser, url)
                self.assertEqual(html.count("admin/css/adminDashboard.css"), 1)
                self.assertNotIn("admin-theme.js", html)
                self.assertNotIn("admin-nav.js", html)
                self.assertNotIn('id="header"', html)
                self.assertIn("admin_interface/css/admin-interface.css", html)
                self.assertIn("admin/js/theme.js", html)

    def test_popup_stylesheet_loads_after_admin_interface_styles(self):
        html = self.get(self.superuser, reverse("admin:auth_group_add") + "?_popup=1")
        self.assertLess(
            html.index("admin_interface/css/admin-interface.css"),
            html.index("admin/css/adminDashboard.css"),
        )

    def test_hero_only_on_the_admin_home(self):
        home = self.get(self.superuser, reverse("admin:index"))
        app_index = self.get(self.superuser, reverse("admin:app_list", args=["auth"]))
        self.assertIn("cb-hero", home)
        self.assertIn("cb-admin-dashboard", home)
        self.assertNotIn("cb-hero", app_index)
        self.assertNotIn("cb-admin-dashboard", app_index)
        self.assertIn("app-auth", app_index)

    def test_sidebar_reuses_native_markup_and_keeps_permissions(self):
        group_list = reverse("admin:auth_group_changelist")
        superuser_html = self.get(self.superuser, reverse("admin:auth_group_add"))
        staff_html = self.get(self.staff_without_perms, reverse("admin:index"))

        self.assertEqual(superuser_html.count('id="nav-sidebar"'), 1)
        self.assertEqual(superuser_html.count('id="toggle-nav-sidebar"'), 1)
        self.assertIn(f'href="{group_list}"', superuser_html)
        self.assertEqual(staff_html.count('id="nav-sidebar"'), 1)
        self.assertNotIn(f'href="{group_list}"', staff_html)

    def test_login_page_has_theme_assets_and_no_sidebar(self):
        self.client.logout()
        html = self.client.get(reverse("admin:login")).content.decode()
        self.assertEqual(html.count("admin/css/adminDashboard.css"), 1)
        self.assertNotIn('id="nav-sidebar"', html)


class AdminResponsiveNavigationSourceTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        static = Path(__file__).resolve().parents[1] / "static" / "admin"
        cls.css = (static / "css" / "adminDashboard.css").read_text(encoding="utf-8")
        cls.js = (static / "js" / "admin-nav.js").read_text(encoding="utf-8")

    def test_breakpoint_matches_django_admin_interface(self):
        self.assertIn('"(max-width: 1279px)"', self.js)
        self.assertIn("@media (max-width: 1279px) {", self.css)
        package_css = (
            Path(admin_interface.__file__).resolve().parent
            / "static"
            / "admin_interface"
            / "css"
            / "nav-sidebar.css"
        ).read_text(encoding="utf-8")
        self.assertIn("@media (max-width:1279px)", package_css)

    def test_drawer_is_accessible_and_reuses_native_elements(self):
        for needle in ("Escape", "inert", "aria-expanded", "aria-controls", "cb-nav-close", "focus()"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.js)
        self.assertNotIn("createElement(\"a\")", self.js)
        self.assertNotIn(".href", self.js)

    def test_add_icon_uses_theme_tokens_instead_of_native_green(self):
        self.assertIn("mask: url(\"../img/icon-addlink.svg\")", self.css)
        self.assertIn("background-color: var(--cb-accent);", self.css)
        self.assertIn("forced-colors: active", self.css)
