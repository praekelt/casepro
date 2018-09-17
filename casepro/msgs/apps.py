from django.apps import AppConfig


class Config(AppConfig):
    name = "casepro.msgs"

    def ready(self):
        from . import signals  # noqa

        from casepro import backend
        backend_class = backend.get_backend_class()
        backend_class.validate_settings()
