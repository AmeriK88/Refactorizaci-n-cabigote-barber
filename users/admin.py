from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile

# Define un inline para UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfiles de usuario'
    fk_name = 'user'

# Extiende UserAdmin para incluir el inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # Opcional: si quieres que el teléfono salga también en la lista de usuarios
    list_display = BaseUserAdmin.list_display + ('get_telefono',)

    def get_telefono(self, obj):
        return obj.userprofile.telefono
    get_telefono.short_description = 'Teléfono'

    # Si tu UserProfile tiene campos obligatorios, evita páginas en blanco:
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Primero “desregistra” el UserAdmin por defecto y luego registra el tuyo
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
