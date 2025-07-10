# core/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model

class CustomSocialAdapter(DefaultSocialAccountAdapter):
    """
     Permite el login si la SocialAccount ya está enlazada.
     Muestra página de error si el e-mail pertenece a un usuario local
     que aún NO ha vinculado Google.
    """

    def pre_social_login(self, request, sociallogin):
        # 1) Si la SocialAccount ya existe para este usuario, no hacemos nada
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if not email:
            return   # proveedor sin e-mail → dejamos que allauth resuelva

        # 2) ¿Hay usuario local con ese e-mail?
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return   

        # 3) ¿Tiene YA enlace con este proveedor?
        if SocialAccount.objects.filter(
            user=user,
            provider=sociallogin.account.provider
        ).exists():
            return  

        # 4) Usuario local SIN vínculo: bloqueamos y mostramos plantilla
        response = render(
            request,
            "socialaccount/social_error.html",
            {
                "error_message": (
                    "Ese correo ya está registrado como cuenta local. "
                    "Inicia sesión con tu usuario y contraseña. "
                )
            },
            status=403
        )
        raise ImmediateHttpResponse(response)
