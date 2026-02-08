from django.contrib.auth.models import User
from django.db import transaction

from users.models import UserProfile


def get_or_create_profile(*, user: User) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "email": user.email or "",
            "nombre": user.first_name or "",
            "apellido": user.last_name or "",
        },
    )
    return profile



@transaction.atomic
def update_profile_data(*, user: User, first_name: str, last_name: str, email: str, telefono: str) -> UserProfile:
    """
    Caso de uso: actualizar datos de perfil (NO password).
    User manda: first_name/last_name/email.
    Profile: telefono + legacy sync (email/nombre/apellido).
    """
    user.first_name = (first_name or "").strip()
    user.last_name = (last_name or "").strip()
    user.email = (email or "").strip()
    user.save(update_fields=["first_name", "last_name", "email"])

    profile = get_or_create_profile(user=user)
    profile.telefono = (telefono or "").strip()

    # compat legacy (sin migración masiva)
    profile.email = user.email
    profile.nombre = user.first_name
    profile.apellido = user.last_name
    profile.save(update_fields=["telefono", "email", "nombre", "apellido"])

    return profile


@transaction.atomic
def deactivate_account(*, user: User) -> None:
    """
    Caso de uso: desactivar cuenta (tu lógica actual).
    """
    UserProfile.objects.filter(user=user).update(
        nombre="",
        apellido="",
        email="",
        telefono="",
    )

    user.is_active = False
    user.email = ""
    user.username = f"deleted_{user.pk}"
    user.save(update_fields=["is_active", "email", "username"])
