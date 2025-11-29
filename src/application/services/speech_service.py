import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)

class SpeechService:
    """Service for Speech-to-Text operations"""

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def speech_to_text(self, language="en-US") -> str:
        """
        Convert speech to text using a microphone.

        Args:
            language: Language code (e.g., 'en-US', 'yo-NG', 'ha-NG', 'sw', 'zu').

        Returns:
            Recognized text or an error message.
        """
        try:
            with sr.Microphone() as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Please speak now...")
                audio = self.recognizer.listen(source)
                print("Processing speech...")
            
            text = self.recognizer.recognize_google(audio, language=language)
            logger.info(f"Speech recognized: {text}")
            return text
        except sr.UnknownValueError:
            logger.error("Speech recognition could not understand audio.")
            return "Could not understand audio."
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return f"Speech recognition service error: {e}"