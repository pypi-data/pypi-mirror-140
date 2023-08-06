from django.apps import AppConfig


class ModelDumpConfig(AppConfig):
    name = 'vtb_django_utils.model_dump'

    def ready(self):
        super().ready()
        self.module.autodiscover()
