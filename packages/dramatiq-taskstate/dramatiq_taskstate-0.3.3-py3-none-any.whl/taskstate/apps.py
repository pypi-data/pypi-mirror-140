from django.apps import AppConfig


class TaskstateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskstate'

    def ready(self):
        import taskstate.receivers # pylint: disable=unused-import
