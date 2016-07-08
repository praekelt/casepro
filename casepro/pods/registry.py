from django.apps import apps
from casepro.pods.pod.plugin import PodConfig


configs = filter(
    lambda app: isinstance(app, PodConfig),
    apps.get_app_configs())


def get_url_patterns():
    return [
        pattern
        for config in configs
        for pattern in config.urlpatterns
    ]


def get_configs():
    return configs
