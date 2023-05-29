from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'gallery_new.api'

    def ready(self):
        super(ApiConfig, self).ready()
        import gallery_new.api.signals