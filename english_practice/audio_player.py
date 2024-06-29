import pygame
from io import BytesIO
from colorama import Fore, Style

class AudioPlayer:
    """
    A class for playing audio data using pygame.

    This class initializes the pygame mixer and provides a method to play audio data.
    It handles various exceptions that may occur during initialization or playback.
    """

    def __init__(self):
        """
        Initialize the AudioPlayer by setting up the pygame mixer.

        Raises:
            pygame.error: If there's an error initializing the pygame mixer.
        """
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"{Fore.RED}Error initializing pygame mixer: {e}{Style.RESET_ALL}")
            raise

    def play_audio(self, audio_data):
        """
        Play the provided audio data.

        This method loads the audio data into a BytesIO buffer, plays it using pygame,
        and waits for the playback to finish. It handles various exceptions that may
        occur during the process.

        Args:
            audio_data (bytes): The audio data to play.

        Raises:
            pygame.error: If there's an error playing the audio.
            Exception: For any unexpected errors during playback.
        """
        if not audio_data:
            print(f"{Fore.YELLOW}Warning: No audio data provided.{Style.RESET_ALL}")
            return
        
        audio_buffer = None
        try:
            audio_buffer = BytesIO(audio_data)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                clock.tick(10)  # Limit the loop to 10 iterations per second
        except pygame.error as e:
            print(f"{Fore.RED}Error playing audio: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        finally:
            pygame.mixer.music.unload()
            if audio_buffer:
                audio_buffer.close()
