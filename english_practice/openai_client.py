from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
from colorama import Fore, Style


class OpenAIClient:
    """
    A client for interacting with OpenAI's API services.

    This class provides methods for generating chat responses, transcribing audio,
    and converting text to speech using OpenAI's models.

    Attributes:
        api_key (str): The OpenAI API key.
        client (OpenAI): The OpenAI client instance.
    """

    def __init__(self):
        """
        Initialize the OpenAIClient.

        Raises:
            ValueError: If the OPENAI_API_KEY environment variable is not set.
        """
        try:
            load_dotenv()
            self.api_key: str = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(f"{Fore.RED}The OPENAI_API_KEY environment variable is not set.{Style.RESET_ALL}")
            self.client: OpenAI = OpenAI(api_key=self.api_key)
        except Exception as e:
            print(f"{Fore.RED}An error occurred during initialization: {e}{Style.RESET_ALL}")
            raise

    def get_response(self, prompt: str, history: list = None, is_translation: bool = False, is_extracting_report: bool = False) -> str:
        """
        Generate a chat response using OpenAI's GPT model.

        Args:
            prompt (str): The user's input prompt.
            history (list, optional): The conversation history. Defaults to None.
            is_translation (bool): Indicates if the request is for translation. Defaults to False.
            is_extracting_report (bool): Indicates if the request is for extracting a report. Defaults to False.

        Returns:
            str: The generated response from the model.
        """
        if is_translation:
            messages: list[dict] = [
                {"role": "system", "content": "You are a translator."}
            ]
        elif is_extracting_report:
            messages: list[dict] = [
                {"role": "system",
                 "content": 
                """You are a report writer in English practice system,
                 you are tasked to write markdown report for the user's progress and activities. 
                 You are given a prompt and the user's history,
                 you are tasked to write a markdown report for the user's progress and activities.
                 You are given a prompt of some activities to the user, such as AI Feedbacks, Results of Vocabulary Quiz, and Achievements.
                 You are tasked to write a markdown report for the user's progress and activities. (ONLY markdown ANSWER! DO NOT WRITE ANYTHING ELSE!)
                 
                 """}
            ]
        else:
            messages: list[dict] = [
                {"role": "system", "content": "You are Lana, a friendly and relatable English tutor in a conversational app with audio. Your responses will be converted to speech using a text-to-speech system. Your goal is to help the user practice English in an engaging and natural way. Ask various interesting questions that encourage the user to talk a lot and maintain a casual atmosphere throughout the conversation. Use informal language and expressions like 'Oh, that's cool!' or 'I've tried that before!' to make the conversation feel more natural. Occasionally, when appropriate, add a touch of humor to keep things light. The session should have exactly 7 exchanges, with the last exchange being a friendly goodbye to the user."}
            ]
        
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            response_stream = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
                temperature=0.8,
                stream=True  # Enable streaming
            )
            
            full_response = ""
            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    # You can process or display each chunk here if needed
                    # print(chunk.choices[0].delta.content, end="", flush=True)
            
            return full_response
        except OpenAIError as e:
            return f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}"
        
    def get_translation(self, text: str) -> str:
        """
        Translate text to English using OpenAI's GPT model.
        """
        if not text:
            return f"{Fore.RED}No text to translate.{Style.RESET_ALL}"
        
        prompt:str = f"""
        You are a highly skilled translator fluent in both English and Arabic. Your task is to accurately translate the provided text from one language to the other.
        If the text is in Arabic, translate it to English. If the text is in English, translate it to Arabic.
        Ensure your translation is precise, concise, and captures the original meaning and tone of the text. Do not include any additional information or commentary.
        Simply provide the translated text.
        
        Text to translate:
        {text}
        """
     
        return self.get_response(prompt, [], is_translation=True)

    def get_feedback(self, history: list) -> str:
        """
        Generate feedback on the conversation using OpenAI's GPT model.

        Args:
            history (list): The conversation history.

        Returns:
            str: The generated feedback.
        """
        feedback_prompt: str = """
        As Lana, the friendly and professional English tutor in a conversational app with audio,
        provide a comprehensive and constructive evaluation of the entire conversation. Be honest but kind in your assessment.
        Focus on the user's grammar, vocabulary, pronunciation, and overall language skills.
        Offer a rating out of 10 for each of these areas.
        Highlight specific areas for improvement with examples from the conversation. 
        Provide actionable advice for future practice sessions, tailored to the user's current level. 
        If the user's responses are too brief, incoherent, or insufficient for meaningful feedback (e.g., one-word answers or responses that cannot be evaluated), do not provide a rating. 
        Instead, kindly inform the user that there wasn't enough material to provide a detailed assessment and encourage them to engage more in future sessions.
        End with an encouraging and motivating message to inspire continued learning and improvement.
        
        When evaluating pronunciation, consider any mispronounced words that were transcribed with correct spellings in [square brackets].
        For example, if you see 'super-market [supermarket]' or 'veg-tables [vegetables]', this indicates a pronunciation error.
        Also, pay attention to filler words, hesitations, and unclear pronunciations that might be represented phonetically.
        For instance, 'wether [weather]' or 'tem-per-a-chur [temperature]' indicate pronunciation challenges.
        Include these observations in your feedback to help the user improve their pronunciation.
        """
        
        return self.get_response(feedback_prompt, history)
    
    def get_report(self, prompt: str) -> str:
       
        return self.get_response(prompt, [], is_extracting_report=True)

    def transcribe_audio(self, filename: str = "input.wav") -> str:
        """
        Transcribe an audio file using OpenAI's Whisper model.

        Args:
            filename (str, optional): The name of the audio file to transcribe. Defaults to "input.wav".

        Returns:
            str: The transcribed text or an error message.
        """
        if not os.path.exists(filename):
            return f"{Fore.RED}Error: Audio file '{filename}' not found.{Style.RESET_ALL}"

        try:
            with open(filename, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    language="en"
                )
            return transcript.text
        except Exception as e:
            error_message = f"{Fore.RED}An error occurred during audio transcription: {e}{Style.RESET_ALL}"
            print(error_message)
            return error_message

    def text_to_speech(self, text: str, voice: str = "nova") -> bytes:
        """
        Convert text to speech using OpenAI's text-to-speech model.

        Args:
            text (str): The text to convert to speech.
            voice (str, optional): The voice to use for text-to-speech. Defaults to "nova".

        Returns:
            bytes: The audio content as bytes, or None if an error occurs.
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            return response.content
        except Exception as e:
            error_message = f"{Fore.RED}An error occurred during text-to-speech conversion: {e}{Style.RESET_ALL}"
            print(error_message)
            return None
