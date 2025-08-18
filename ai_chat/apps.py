from django.apps import AppConfig


class AiChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_chat'

    def ready(self):
        # Register signals
        from . import signals  # noqa: F401
