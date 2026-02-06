from django.apps import AppConfig
from django.contrib import admin

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        admin.site.index_template = "admin/index.html"
