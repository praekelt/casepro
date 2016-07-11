from django.conf.urls import url
from django.http import JsonResponse
from casepro.pods.pod.plugin import PodConfig


def get_dummy(request):
    # takes in case_id as query param
    return JsonResponse({'foo': 23})


class DummyPodConfig(PodConfig):
    name = 'casepro.pods.dummy'
    verbose_name = 'Dummy'
    scripts = ('static/coffee/dummy.coffee',)
    urlpatterns = [url(r'dummy$', get_dummy, name='get_dummy')]
    controller = 'DummyPodController'
    directive = 'dummy-pod'
