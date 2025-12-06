from gtts import gTTS
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class TTSService:
    """Service for Text-to-Speech operations"""
    
    def text_to_speech(self, text: str, language="en") -> str:
        """
        Convert text to speech and save it.
        
        Args:
            text: Text to convert to speech.
            language: Language code (e.g., 'en', 'yo', 'ha', 'sw', 'zu').
        
        Returns:
            Path to the generated audio file.
        """
        temp_dir = tempfile.gettempdir()
        filename = f"tts_{os.urandom(8).hex()}.mp3"
        file_path = os.path.join(temp_dir, filename)
        
        try:
            tts = gTTS(text=text, lang=language)
            tts.save(file_path)
            logger.info(f"Text-to-speech file saved: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            raise