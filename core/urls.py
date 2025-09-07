from django.urls import path
from django.views.generic import TemplateView
from .views import lanzar_recordatorios

urlpatterns = [
    path('lanzar-recordatorios/', lanzar_recordatorios, name='lanzar_recordatorios'),
    path("cookies/",    TemplateView.as_view(template_name="legal/cookies.html"),    name="cookies"),
    path("privacidad/", TemplateView.as_view(template_name="legal/privacidad.html"), name="privacidad"),
]
