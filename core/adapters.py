from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.exceptions import ImmediateHttpResponse  
from django.shortcuts import render
from django.contrib.auth import get_user_model

class CustomSocialAdapter(DefaultSocialAccountAdapter):
    """
     Permite el login si la SocialAccount ya está enlazada.
     Muestra página de error si el e-mail pertenece a un usuario local
     que aún NO ha vinculado Google.
    """

    def pre_social_login(self, request, sociallogin):
        # 0) "connect" explicitly skips this check
        if sociallogin.state.get("process") == "connect":
            return

        # 1) If SocialAccount / nothing to do
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if not email:
            return   

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return  

        # 2) If user email already logged in, allow
        if request.user.is_authenticated and request.user == user:
            return

        # 3) If SocialAccount already exists for this user, allow
        if SocialAccount.objects.filter(user=user,
                                        provider=sociallogin.account.provider
                                        ).exists():
            return

        # 4) Block login if email is already registered as a local user
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
