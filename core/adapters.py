from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.exceptions import ImmediateHttpResponse   # importa desde allauth.exceptions
from django.shortcuts import render
from django.contrib.auth import get_user_model

class CustomSocialAdapter(DefaultSocialAccountAdapter):
    """
     Permite el login si la SocialAccount ya está enlazada.
     Muestra página de error si el e-mail pertenece a un usuario local
     que aún NO ha vinculado Google.
    """

    def pre_social_login(self, request, sociallogin):
        # 0) Si viene de un "connect" explícito, permitir siempre
        if sociallogin.state.get("process") == "connect":
            return

        # 1) Si la SocialAccount ya existe para este usuario, nada que hacer
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if not email:
            return   # proveedor sin e‑mail → deja que allauth gestione

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return   # e‑mail nuevo → deja que allauth cree usuario

        # 2) Si el usuario YA está logeado y coincide con ese e‑mail, permitir
        if request.user.is_authenticated and request.user == user:
            return

        # 3) Si ese user ya tiene SocialAccount para este provider, permitir
        if SocialAccount.objects.filter(user=user,
                                        provider=sociallogin.account.provider
                                        ).exists():
            return

        # 4) Usuario local sin vínculo: bloqueamos
        response = render(
            request,
            "socialaccount/social_error.html",
            {
                "error_message": (
                    "¡Chacho! Ese correo ya está registrado como cuenta local. "
                    "Inicia sesión con tu usuario y contraseña y vincula "
                    "Google desde tu perfil."
                )
            },
            status=403
        )
        raise ImmediateHttpResponse(response)
