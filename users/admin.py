from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import UserProfile

# ─── 0) Des‐registrar el admin por defecto ───────────────────
admin.site.unregister(User)


# ─── 1) Inline del perfil ─────────────────────────────────――
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Perfil'
    extra = 0
    fieldsets = (
        (_('Contacto'),    {'fields': ('telefono', 'email')}),
        (_('Datos extra'), {'fields': ('nombre', 'apellido')}),
    )


# ─── 2) Helper para iconos booleanos ✔/✖ ────────────────────
def bool_icon(flag: bool,
              yes='✔️', no='❌',
              color_yes='#28a745', color_no='#dc3545') -> str:
    char  = yes if flag else no
    color = color_yes if flag else color_no
    return mark_safe(f'<span style="color:{color}; font-weight:bold">{char}</span>')


# ─── 3) Admin personalizado ─────────────────────────────────
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'tel_badge',      # teléfono
        'staff_icon',     # staff?
        'active_icon',    # activo?
        'super_icon',     # super?
        'last_login', 'date_joined',
    )
    list_select_related = ('userprofile',)
    list_filter   = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name',
                     'email', 'userprofile__telefono')
    ordering      = ('-date_joined',)
    list_per_page = 40

    inlines         = (UserProfileInline,)
    readonly_fields = ('last_login', 'date_joined')


    # ── columnas personalizadas ──────────────────────────────
    @admin.display(description='Teléfono', ordering='userprofile__telefono')
    def tel_badge(self, obj):
        tel = getattr(obj.userprofile, 'telefono', '') or '—'
        return format_html('<span class="badge bg-secondary">{}</span>', tel[:15])

    @admin.display(description='Staff', ordering='is_staff')
    def staff_icon(self, obj):
        return bool_icon(obj.is_staff)

    @admin.display(description='Activo', ordering='is_active')
    def active_icon(self, obj):
        return bool_icon(obj.is_active)

    @admin.display(description='Super', ordering='is_superuser')
    def super_icon(self, obj):
        return bool_icon(obj.is_superuser, yes='★')

    # ── acción masiva ────────────────────────────────────────
    @admin.action(description='Activar usuarios seleccionados')
    def activar_cuentas(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} cuenta(s) activadas.')

    # Evita inline vacío al crear
    def get_inline_instances(self, request, obj=None):
        return super().get_inline_instances(request, obj) if obj else []

    # ── CSS específico ───────────────────────────────────────
    class Media:
        css = {
            'all': (
                'admin/css/adminDashboard.css', 
            )
        }


# ─── 4) Registrar la versión mejorada ───────────────────────
admin.site.register(User, UserAdmin)
