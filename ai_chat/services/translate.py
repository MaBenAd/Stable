from django.conf import settings

try:
    from deep_translator import GoogleTranslator
except Exception:  # pragma: no cover
    GoogleTranslator = None


def translate_prompt_to_target(prompt: str) -> str:
    """
    Traduit le prompt vers la langue cible (par défaut en) si activé.
    Si la bibliothèque de traduction n'est pas disponible, retourne le prompt original.
    """
    if not getattr(settings, 'TRANSLATE_PROMPTS', True):
        return prompt

    if not GoogleTranslator:
        return prompt

    target = getattr(settings, 'TRANSLATE_TARGET_LANG', 'en')
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(prompt)
        return translated or prompt
    except Exception:
        return prompt


