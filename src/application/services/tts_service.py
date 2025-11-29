from gtts import gTTS
import os
import tempfile
import logging
import pygame

logger = logging.getLogger(__name__)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

class TTSService:
    """Service for Text-to-Speech operations"""

    def text_to_speech(self, text: str, language="en", play_audio=True) -> str:
        """
        Convert text to speech and optionally play it.

        Args:
            text: Text to convert to speech.
            language: Language code (e.g., 'en', 'yo', 'ha', 'sw', 'zu').
            play_audio: If True, plays the audio immediately. If False, just saves the file.

        Returns:
            Path to the generated audio file.
        """
        temp_dir = tempfile.gettempdir()
        filename = f"tts_{os.urandom(8).hex()}.mp3"
        file_path = os.path.join(temp_dir, filename)

        try:
            # Generate speech
            tts = gTTS(text=text, lang=language)
            tts.save(file_path)
            logger.info(f"Text-to-speech file saved: {file_path}")
            
            # Play audio if requested
            if play_audio:
                logger.info("Playing audio...")
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                
                # Wait for audio to finish playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                logger.info("Audio playback completed")
            
            return file_path
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            raise
    
    def play_audio_file(self, file_path: str):
        """
        Play an existing audio file.
        
        Args:
            file_path: Path to the audio file to play.
        """
        try:
            logger.info(f"Playing audio file: {file_path}")
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            logger.info("Audio playback completed")
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            raise