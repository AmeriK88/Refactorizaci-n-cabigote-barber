from pathlib import Path

import admin_interface
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.loader import get_template
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from services.models import Servicio


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

    def test_dashboard_only_on_the_admin_home(self):
        home = self.get(self.superuser, reverse("admin:index"))
        app_index = self.get(self.superuser, reverse("admin:app_list", args=["auth"]))
        self.assertIn("cb-dash-hero", home)
        self.assertIn("cb-admin-dashboard", home)
        self.assertNotIn("cb-dash-hero", app_index)
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


class AdminChangelistStylesheetTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        path = Path(__file__).resolve().parents[1] / "static" / "admin" / "css" / "adminDashboard.css"
        cls.css = path.read_text(encoding="utf-8")
        cls.block = cls.css.split("TABLAS Y LISTADOS (fase 3B)", 1)[1].split("@keyframes cb-spin", 1)[0]

    def test_changelist_selectors_target_native_django_markup(self):
        for selector in (
            "body.admin-interface #result_list",
            "body.admin-interface #toolbar",
            "body.admin-interface #changelist .actions",
            "body.admin-interface #changelist .paginator",
            "body.admin-interface #changelist-filter",
            "td.num",
            "tr.selected",
            "th.sorted",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, self.block)

    def test_changelist_block_uses_tokens_only(self):
        self.assertNotRegex(self.block, r"#[0-9a-fA-F]{3,6}\b")
        self.assertNotIn("!important", self.block)
        self.assertNotIn("@import", self.block)

    def test_changelist_block_covers_accessibility_and_responsive(self):
        for needle in (":focus-visible", "prefers-reduced-motion", "forced-colors: active",
                       "max-width: 1023px", "max-width: 767px", "overflow-x: auto", "accent-color"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.block)

    def test_changelist_does_not_hide_native_controls(self):
        self.assertNotRegex(self.block, r"display:\s*none;[^}]*\}\s*$")
        for hidden in ("#changelist-filter {\n  display: none", ".actions {\n  display: none"):
            self.assertNotIn(hidden, self.block)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class AdminChangelistRenderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.superuser = user_model.objects.create_superuser(
            username="root", email="root@example.com", password="Test-pass-12345"
        )
        cls.staff_without_perms = user_model.objects.create_user(
            username="staff", email="staff@example.com", password="Test-pass-12345", is_staff=True
        )
        for i in range(45):
            user_model.objects.create_user(
                username=f"cliente{i:02d}", email=f"c{i}@example.com", password="Test-pass-12345"
            )

    def get(self, user, url, status=200):
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)
        return response.content.decode()

    def test_native_changelist_structure_is_preserved_for_users(self):
        html = self.get(self.superuser, reverse("admin:auth_user_changelist"))
        for marker in ('id="result_list"', 'id="changelist-search"', 'id="changelist-filter"',
                       'class="actions"', 'class="paginator"', 'id="searchbar"', "action-select"):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)
        self.assertEqual(html.count("admin/css/adminDashboard.css"), 1)
        self.assertIn("admin/css/changelists.css", html)

    def test_search_ordering_and_pagination_keep_working(self):
        base = reverse("admin:auth_user_changelist")
        self.assertIn("cliente07", self.get(self.superuser, base + "?q=cliente07"))
        self.assertIn("sorted ascending", self.get(self.superuser, base + "?o=1"))
        self.assertIn("sorted descending", self.get(self.superuser, base + "?o=-1"))
        self.assertIn('class="this-page"', self.get(self.superuser, base + "?p=1"))

    def test_filters_and_empty_state_render(self):
        base = reverse("admin:auth_user_changelist")
        html = self.get(self.superuser, base + "?is_staff__exact=1")
        self.assertRegex(html, r'<option[^>]*selected|class="selected"')
        empty = self.get(self.superuser, base + "?q=zzz-no-existe")
        self.assertNotIn('id="result_list"', empty)
        self.assertIn('class="paginator"', empty)
        self.assertNotIn("action-select", empty)

    def test_group_changelist_renders_for_superuser(self):
        html = self.get(self.superuser, reverse("admin:auth_group_changelist"))
        self.assertIn('id="changelist"', html)
        self.assertEqual(html.count("admin/js/admin-theme.js"), 1)

    def test_staff_without_permissions_cannot_see_changelists(self):
        self.get(self.staff_without_perms, reverse("admin:auth_user_changelist"), status=403)


class StatusBadgeTests(SimpleTestCase):
    def test_status_badge_has_text_icon_and_classes(self):
        from core.admin_badges import status_badge
        yes, no = str(status_badge(True)), str(status_badge(False))
        self.assertIn("cb-badge--yes", yes)
        self.assertIn("cb-badge--no", no)
        self.assertIn('aria-hidden="true"', yes)
        self.assertNotIn("style=", yes + no)
        self.assertNotEqual(yes, no)
        self.assertRegex(yes, r"</span>\w+</span>$")

    def test_rating_badge_is_textual_and_clamped(self):
        from core.admin_badges import rating_badge
        html = str(rating_badge(4))
        self.assertIn("4/5", html)
        self.assertIn("★★★★☆", html)
        self.assertIn("5/5", str(rating_badge(99)))
        self.assertIn("0/5", str(rating_badge(None)))

    def test_badges_escape_user_data(self):
        from core.admin_badges import neutral_badge
        html = str(neutral_badge("<script>alert(1)</script>"))
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_admins_no_longer_use_emojis_or_literal_colors(self):
        root = Path(__file__).resolve().parents[1]
        for rel in ("users/admin.py", "reviews/admin.py"):
            source = (root / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertNotIn("mark_safe", source)
                self.assertNotRegex(source, r"#[0-9a-fA-F]{6}")
                self.assertNotIn("⭐", source)


class AdminBadgeAndDestructiveActionStylesTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        path = Path(__file__).resolve().parents[1] / "static" / "admin" / "css" / "adminDashboard.css"
        cls.css = path.read_text(encoding="utf-8")

    def test_badge_variants_use_tokens(self):
        for variant in ("yes", "no", "rating", "neutral"):
            self.assertIn(f".cb-badge--{variant}", self.css)

    def test_destructive_action_detected_by_technical_value_not_translated_text(self):
        self.assertIn('option[value="delete_selected"]:checked', self.css)
        self.assertNotIn("Delete selected", self.css)
        self.assertNotIn("Eliminar", self.css)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class AdminBadgeRenderingTests(TestCase):
    def test_user_and_review_changelists_render_badges(self):
        user_model = get_user_model()
        root = user_model.objects.create_superuser("root", "r@example.com", "Test-pass-12345")
        self.client.force_login(root)
        html = self.client.get(reverse("admin:auth_user_changelist")).content.decode()
        self.assertIn("cb-badge--yes", html)
        self.assertNotIn("color:#28a745", html)
        self.assertEqual(self.client.get(reverse("admin:reviews_resena_changelist")).status_code, 200)


class AdminFormsStylesheetTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        path = Path(__file__).resolve().parents[1] / "static" / "admin" / "css" / "adminDashboard.css"
        cls.block = path.read_text(encoding="utf-8").split("FORMULARIOS (fase 3C)", 1)[1].split("@keyframes cb-spin", 1)[0]

    def test_forms_block_uses_tokens_only(self):
        self.assertNotRegex(self.block, r"#[0-9a-fA-F]{3,6}\b")
        self.assertNotIn("!important", self.block)
        self.assertNotIn("@import", self.block)

    def test_forms_block_targets_native_markup(self):
        for selector in ("fieldset.module", ".form-row", ".submit-row", "a.deletelink",
                         ".errornote", "ul.errorlist", ".selector", ".calendarbox", ".inline-group",
                         "delete-confirmation"):
            with self.subTest(selector=selector):
                self.assertIn(selector, self.block)

    def test_forms_block_covers_accessibility_and_responsive(self):
        for needle in (":focus-visible", "prefers-reduced-motion", "forced-colors: active",
                       "max-width: 767px", "min-height: 44px", "accent-color"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.block)

    def test_errors_do_not_rely_on_color_alone(self):
        self.assertIn("ul.errorlist li::before", self.block)
        self.assertIn("label.required::after", self.block)

    def test_delete_confirmation_targets_form_under_content(self):
        # En Django 5.2 el formulario cuelga de #content, no de #content-main.
        self.assertIn("delete-confirmation #content > form", self.block)
        self.assertNotIn("delete-confirmation #content-main", self.block)

    def test_dual_selector_can_shrink_and_lookup_is_touch_sized(self):
        self.assertRegex(self.block, r"\.selector select\s*\{\s*min-width: 0;")
        self.assertIn("a.related-lookup", self.block)
        self.assertIn("width: 28px", self.block)


@override_settings(STORAGES=STATIC_STORAGES, SECURE_SSL_REDIRECT=False)
class AdminFormsRenderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_superuser("root", "r@example.com", "Test-pass-12345")

    def get(self, url, status=200):
        self.client.force_login(self.superuser)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)
        return response.content.decode()

    def test_add_forms_keep_native_structure_and_load_css_once(self):
        for name in ("auth_user_add", "auth_group_add", "services_servicio_add", "products_imagen_add",
                     "appointments_cita_add", "reviews_resena_add"):
            with self.subTest(name=name):
                html = self.get(reverse(f"admin:{name}"))
                for marker in ("csrfmiddlewaretoken", 'class="submit-row"', "<fieldset", 'class="form-row'):
                    self.assertIn(marker, html)
                self.assertEqual(html.count("admin/css/adminDashboard.css"), 1)
                self.assertEqual(html.count("admin/js/admin-theme.js"), 1)

    def test_change_form_with_inline_renders(self):
        html = self.get(reverse("admin:auth_user_change", args=[self.superuser.pk]))
        self.assertIn("inline-group", html)
        self.assertIn('class="submit-row"', html)

    def test_validation_errors_are_rendered_with_text(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("admin:auth_group_add"), {"name": ""})
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("errornote", html)
        self.assertIn("errorlist", html)

    def test_delete_confirmation_renders(self):
        html = self.get(reverse("admin:auth_user_delete", args=[self.superuser.pk]))
        self.assertIn("delete-confirmation", html)
        self.assertIn("csrfmiddlewaretoken", html)
        self.assertNotIn('id="content-main"', html)

    def test_date_and_time_widgets_use_native_django_calendar(self):
        html = self.get(reverse("admin:appointments_cita_add"))
        for script in ("admin/js/calendar.js", "admin/js/admin/DateTimeShortcuts.js"):
            self.assertEqual(html.count(script), 1)
        self.assertIn('class="vDateField"', html)
        self.assertIn('class="vTimeField"', html)

    def test_forms_require_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.superuser)
        response = client.post(reverse("admin:auth_group_add"), {"name": "x"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Group.objects.filter(name="x").exists())

    def test_staff_without_permissions_cannot_open_or_post_forms(self):
        staff = get_user_model().objects.create_user("staff", "s@example.com", "Test-pass-12345", is_staff=True)
        self.client.force_login(staff)
        for name in ("auth_group_add", "services_servicio_add"):
            url = reverse(f"admin:{name}")
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {"name": "y"}).status_code, 403)
        self.assertFalse(Group.objects.filter(name="y").exists())

    def test_invalid_post_shows_errors_and_saves_nothing(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("admin:services_servicio_add"), {"nombre": "", "precio": "-5"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errornote")
        self.assertFalse(Servicio.objects.exists())

    def test_valid_service_saves_with_each_save_button(self):
        self.client.force_login(self.superuser)
        for i, button in enumerate(("_save", "_continue", "_addanother")):
            response = self.client.post(reverse("admin:services_servicio_add"), {
                "nombre": f"S{i}", "descripcion": "d", "precio": "10.00", "duracion": "30", button: "1",
            })
            self.assertEqual(response.status_code, 302, button)
        self.assertEqual(Servicio.objects.count(), 3)
