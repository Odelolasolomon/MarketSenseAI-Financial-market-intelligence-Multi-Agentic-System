from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for text translation"""

    def __init__(self):
        # deep-translator creates translator instances per request
        pass

    def translate_text(self, text: str, src: str, dest: str) -> str:
        """
        Translate text from one language to another.

        Args:
            text: Text to translate.
            src: Source language code (e.g., 'en', 'yo', 'ha', 'sw', 'zu').
            dest: Destination language code.

        Returns:
            Translated text.
        """
        try:
            translator = GoogleTranslator(source=src, target=dest)
            translated_text = translator.translate(text)
            logger.info(f"Translated text: {translated_text}")
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise