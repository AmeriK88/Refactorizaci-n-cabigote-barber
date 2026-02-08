from django.contrib.auth.models import User
from django.db import transaction

from users.models import UserProfile


@transaction.atomic
def register_user(*, username: str, password: str, email: str, first_name: str, last_name: str, phone: str) -> User:
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    # Garantiza profile (sin signals)
    UserProfile.objects.create(
        user=user,
        telefono=phone,
        # compat: mantenemos espejo por ahora
        email=email,
        nombre=first_name,
        apellido=last_name,
    )
    return user
