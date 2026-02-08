from django.contrib.auth.models import User

from users.models import UserProfile


def get_profile(*, user: User) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"email": user.email or "", "nombre": user.first_name or "", "apellido": user.last_name or ""},
    )
    return profile
