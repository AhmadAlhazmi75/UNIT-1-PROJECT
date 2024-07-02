import pyaudio
import wave
import threading
from colorama import Fore, Style

"""
    Notes: 
    The role of threading in this code is :
    - It enables continuous audio recording in the background while the main thread waits for user input to stop the recording.
    - It prevents the program from blocking during the recording process, ensuring responsiveness to user commands.
    """
class AudioRecorder:
    """
    A class for recording audio data using PyAudio.

    This class provides functionality to record audio input from the default microphone
    and save it to a WAV file.
    Attributes:
        CHUNK (int): The number of audio frames per buffer.
        FORMAT (int): The sample format (e.g., pyaudio.paInt16).
        CHANNELS (int): The number of audio channels (1 for mono, 2 for stereo).
        RATE (int): The sampling rate in Hz.
    """

    def __init__(self) -> None:
        """Initialize the AudioRecorder with default audio parameters."""
        self.CHUNK: int = 1024
        self.FORMAT: int = pyaudio.paInt16
        self.CHANNELS: int = 1
        self.RATE: int = 44100

    def record_audio(self, filename: str = "input.wav") -> None:
        """
        Record audio from the default microphone and save it to a file.

        This method starts a recording session, allowing the user to control when to start
        and stop recording. The recorded audio is saved to the specified filename.

        Args:
            filename (str, optional): The name of the file to save the audio data to. Defaults to "input.wav".

        Raises:
            IOError: If there's an error during audio recording or file writing.
        """
        p: pyaudio.PyAudio = None
        stream: pyaudio.Stream = None

        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
        except Exception as e:
            print(f"{Fore.RED}Error initializing PyAudio or opening audio stream: {e}{Style.RESET_ALL}")
            if p:
                p.terminate()
            return

        print(f"{Fore.YELLOW}Press Enter to start recording. Press Enter again to stop.{Style.RESET_ALL}")
        input()  # Wait for Enter to start recording

        print(f"{Fore.GREEN}Recording... Press Enter to stop.{Style.RESET_ALL}")
        frames: list[bytes] = []
        recording: bool = True

        def record() -> None:
            """
            Internal function to continuously record audio data.

            This function runs in a separate thread and appends audio data to the frames list
            until the recording flag is set to False.
            """
            nonlocal recording
            while recording:
                try:
                    data: bytes = stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except IOError as e:
                    if e.errno == pyaudio.paInputOverflowed:
                        print(f"{Fore.YELLOW}Warning: Audio input overflowed{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Error recording audio: {e}{Style.RESET_ALL}")
                        recording = False
                except Exception as e:
                    print(f"{Fore.RED}Unexpected error during recording: {e}{Style.RESET_ALL}")
                    recording = False

        # Start recording in a separate thread
        record_thread: threading.Thread = threading.Thread(target=record)
        record_thread.start()

        # Wait for user to press Enter to stop recording
        input()
        recording = False

        # Wait for the recording thread to finish
        record_thread.join()

        print(f"{Fore.GREEN}Recording stopped.{Style.RESET_ALL}")

        if stream:
            stream.stop_stream()
            stream.close()
        if p:
            p.terminate()

        if frames:
            self.__save_audio_to_file(filename, p, frames)
        else:
            print(f"{Fore.RED}No audio data recorded.{Style.RESET_ALL}")

    def __save_audio_to_file(self, filename: str, p: pyaudio.PyAudio, frames: list[bytes]) -> None:
        """
        Save the recorded audio data to a WAV file.

        Args:
            filename (str): The name of the file to save the audio data to.
            p (pyaudio.PyAudio): The PyAudio instance used for recording.
            frames (list[bytes]): The list of recorded audio frames.

        Raises:
            IOError: If there's an error writing the audio data to the file.
        """
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(p.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))
            print(f"{Fore.GREEN}Audio saved to {filename}{Style.RESET_ALL}")
        except IOError as e:
            print(f"{Fore.RED}Error saving audio to file: {e}{Style.RESET_ALL}")
