from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoLocalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_locales'
    verbose_name = _("django_locales.app")
