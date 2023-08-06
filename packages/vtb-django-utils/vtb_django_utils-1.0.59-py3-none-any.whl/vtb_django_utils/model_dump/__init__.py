from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules('model_dump.dump')
    autodiscover_modules('model_dump.load')


default_app_config = 'vtb_django_utils.model_dump.apps.ModelDumpConfig'
