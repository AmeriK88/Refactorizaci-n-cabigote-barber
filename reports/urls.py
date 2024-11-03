from django.urls import path
from . import views

urlpatterns = [
    path('reporte-mensual/', views.generate_monthly_report, name='reporte_mensual'),
]
