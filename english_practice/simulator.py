import os
import signal
import atexit
from art import text2art
from colorama import Fore, Style
from simple_term_menu import TerminalMenu

from .openai_client import OpenAIClient
from .feedback_manager import FeedbackManager
from .audio_recorder import AudioRecorder
from .audio_player import AudioPlayer
from .external_assets import ExternalAssets
from .vocabulary_builder import VocabularyBuilder
from .dictionary_search import DictionarySearch
from .authentication import GoogleAuthenticator
from .achievements import Achievements
from .report_generator import ReportGenerator

class EnglishPracticeSimulator:
    """
    Main entry point for the English practice simulator.
    Manages various components and provides a user interface for different functionalities.
    """
    def __init__(self):
        try:
            # Initialize all components
            self.openai_client = OpenAIClient()
            self.feedback_manager = FeedbackManager()
            self.audio_recorder = AudioRecorder()
            self.audio_player = AudioPlayer()
            self.external_assets = ExternalAssets("English Grammar Cheatsheet", "https://sprachinstitut-berlin.de/wp-content/uploads/2019/12/EnglischGrammatikSprachinstitutCheatsheetA3.pdf")
            self.vocabulary_builder = VocabularyBuilder()
            self.dictionary_search = DictionarySearch()
            self.google_authenticator = GoogleAuthenticator()
            self.achievements = Achievements()
            
            # Register cleanup functions
            atexit.register(self.__cleanup)
            signal.signal(signal.SIGINT, self.__signal_handler)
        except Exception as e:
            print(f"Error initializing EnglishPracticeSimulator: {str(e)}")
            raise

    def __cleanup(self):
        """Remove user_id.json and token.json files."""
        try:
            for file in ['user_id.json', 'token.json']:
                if os.path.exists(file):
                    os.remove(file)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def __signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) signal."""
        print("\nReceived interrupt signal. Cleaning up...")
        self.__cleanup()
        exit(0)

    def run(self):
        """Main loop for the English practice simulator."""
        history = []
        
        menu_options = [
            "Start English Practice",
            "Search for a specific word",
            "AI Translator",
            "English Grammar Cheatsheet",
            "Vocabulary Builder",
            "Display AI Feedbacks",
            "Display Vocabulary Quiz Results",
            "Display Achievements",
            "Export Report",
            "Exit"
        ]
        
        while True:
            try:
                self.__clear_console()
                print(text2art(f"WELCOME", "3d_diagonal"))
                print(f"{Fore.CYAN}Menu:{Style.RESET_ALL}")
                
                terminal_menu = TerminalMenu(menu_options, title="Select an option")
                choice = terminal_menu.show()
                
                if choice == 9:  # Exit
                    self.google_authenticator.logout()
                    self.__cleanup()
                    break
                elif choice == 8:  # Export Report
                    self.__export_report()
                elif choice == 7:  # Display Achievements
                    self.achievements.display_all_achievements()
                elif choice == 6:  # Display Vocabulary Quiz Results
                    self.vocabulary_builder.display_vocabulary_quiz_results()
                elif choice == 5:  # Display AI Feedbacks
                    self.feedback_manager.display_feedbacks()
                elif choice == 4:  # Vocabulary Builder
                    self.vocabulary_builder.generate_quiz()
                elif choice == 3:  # English Grammar Cheatsheet
                    self.external_assets.open_in_browser()
                elif choice == 2:  # Translation
                    text = input(f"{Fore.YELLOW}Enter the text to translate: {Style.RESET_ALL}")
                    translated_text = self.openai_client.get_translation(text)
                    print(f"{Fore.GREEN}Translation: {translated_text}{Style.RESET_ALL}")
                elif choice == 1:  # Search for a specific word
                    self.dictionary_search.search_dictionary()
                elif choice == 0:  # Start English Practice
                    self.__start_practice_session(history)
                    history = []  # Reset history for new practice session
                
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

    def __clear_console(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def __start_practice_session(self, history):
        """Start an English practice session with Lana."""
        try:
            name = input(f"{Fore.YELLOW}Enter your name (or press Enter to return to the main menu): {Style.RESET_ALL} ")
            if name == "":
                return

            print(f"{Fore.YELLOW}Choose input method for this session:{Style.RESET_ALL}")
            print("1. Record audio")
            print("2. Type text")
            input_choice = input("Enter your choice (1 or 2): ")
            use_audio = (input_choice == "1")

            prompt = f"""
            You are Lana, an engaging and friendly English tutor in a conversational app with audio.
            Start by warmly greeting {name} and begin the English practice session.
            Keep the conversation light and enjoyable with occasional humor when appropriate. Ask one thought-provoking question at a time that encourages {name} to provide detailed responses and practice their English skills.
            Laugh and say 'Hahaha' only when the user says something genuinely funny to maintain a natural flow of conversation.
            There will be exactly 7 exchanges, with the last one being a friendly goodbye to the user.
            If the user asks something off-topic, gently guide them back to the main topic while maintaining a positive tone.
            Also, if the user provides very brief answers, such as one-word responses, kindly remind them that more detailed answers will help them learn and get the full benefits of having you as their English Coach.
            Throughout the session, provide encouragement and praise for their efforts to keep them motivated and engaged in the learning process.
            """
            
            # Start the practice session with Lana asking the first question
            response = self.openai_client.get_response(prompt, history)
            self.__display_and_play_response(response)
            history.append({"role": "assistant", "content": response})
            
            for exchange_count in range(1, 7):
                user_input = self.__get_user_input(use_audio)
                history.append({"role": "user", "content": user_input})
                
                response = self.openai_client.get_response(
                    f"Continue the English practice session based on the user's response. Ask follow-up questions or introduce new topics to keep the conversation engaging and fun. There are {7 - exchange_count} exchanges left, including this one. If this is the last exchange, make sure to say goodbye to the user.",
                    history
                )
                self.__display_and_play_response(response)
                history.append({"role": "assistant", "content": response})
                
                print(f"{Fore.YELLOW}Exchange {exchange_count + 1}/7{Style.RESET_ALL}")
            
            self.__provide_feedback(history)
        except Exception as e:
            print(f"An error occurred during the practice session: {str(e)}")

    def __display_and_play_response(self, response):
        """Display Lana's response and play it as audio."""
        try:
            print(f"{Fore.GREEN}Lana: {response}{Style.RESET_ALL}")
            audio_data = self.openai_client.text_to_speech(response)
            if audio_data:
                self.audio_player.play_audio(audio_data)
        except Exception as e:
            print(f"Error displaying or playing response: {str(e)}")

    def __get_user_input(self, use_audio):
        """Get user input either by recording audio or typing text."""
        try:
            if use_audio:
                print(f"{Fore.YELLOW}Press Enter to start recording your response. Press Enter again to stop.{Style.RESET_ALL}")
                input()  # Wait for Enter to start recording
                self.audio_recorder.record_audio()
                user_input = self.openai_client.transcribe_audio()
            else:
                user_input = input(f"{Fore.YELLOW}Type your response: {Style.RESET_ALL}")
            
            print(f"{Fore.BLUE}You: {user_input}{Style.RESET_ALL}")
            return user_input
        except Exception as e:
            print(f"Error getting user input: {str(e)}")
            return ""

    def __provide_feedback(self, history):
        """Generate and display feedback for the practice session."""
        try:
            feedback = self.openai_client.get_feedback(history)
            print(f"\n{Fore.MAGENTA}Practice Session Feedback:{Style.RESET_ALL}")
            print(feedback)
            
            feedback_audio = self.openai_client.text_to_speech(feedback)
            if feedback_audio:
                print(f"{Fore.YELLOW}Playing feedback audio...{Style.RESET_ALL}")
                self.audio_player.play_audio(feedback_audio)
            
            self.feedback_manager.save_feedback(feedback)
            print(f"{Fore.YELLOW}Feedback has been saved to 'english_practice_feedback.json'{Style.RESET_ALL}")
        except Exception as e:
            print(f"Error providing feedback: {str(e)}")

    def __export_report(self):
        """Export a report of the user's progress and activities."""
        try:
            print(f"{Fore.YELLOW}Exporting report...{Style.RESET_ALL}")
            
            # get user_id
            user_id = self.google_authenticator.get_stored_user_id()
            # get feedbacks
            feedbacks = [feedback for feedback in self.feedback_manager.display_feedbacks()]
            # get vocabulary quizzes
            vocabulary_quizzes = [quiz for quiz in self.vocabulary_builder.display_vocabulary_quiz_results()]
            # get achievements
            achievements = [achievement for achievement in self.achievements.display_achievements()]
            
            prompt = f"""
            Generate a comprehensive and personalized progress report for the user with ID {user_id}. The report should be structured as follows:

            1. Executive Summary:
               - Provide a brief overview of the user's overall progress and key achievements.

            2. Detailed Analysis of AI Feedbacks:
               - Analyze the following AI feedbacks: {feedbacks}
               - Identify recurring themes, areas of improvement, and notable progress.
               - Highlight specific examples of growth in language skills.

            3. Vocabulary Quiz Performance:
               - Evaluate the user's performance in vocabulary quizzes: {vocabulary_quizzes}
               - Calculate and present statistics such as average score, improvement over time, and areas of strength/weakness.
               - Identify any patterns in word categories or difficulty levels the user excels in or struggles with.

            4. Achievement Milestones:
               - List and describe the achievements unlocked by the user: {achievements}
               - Explain the significance of each achievement and how it relates to the user's language learning journey.
               - Suggest upcoming achievements the user might aim for next.

            5. Overall Progress Assessment:
               - Synthesize information from all sections to provide a comprehensive view of the user's English language development.
               - Identify key strengths and areas that need more focus.

            6. Personalized Improvement Plan:
               - Based on the analysis, recommend specific areas for the user to focus on.
               - Suggest tailored learning strategies and resources for each area of improvement.
               - Provide a roadmap for the next steps in the user's language learning journey.

            7. Motivational Conclusion:
               - End with an encouraging message that acknowledges the user's efforts and progress.
               - Set positive expectations for future growth and learning.

            Please ensure the report is written in a professional yet engaging tone, using clear language and avoiding technical jargon. The report should be detailed and analytical, transforming the raw data into meaningful insights and actionable advice for the user.
            and if the user do not have enough quizzes and results, tell the user to please practice more.
            """
            
            
            # Generate the report
            report_generator = ReportGenerator(self.google_authenticator.get_stored_user_id())
            if os.path.exists("user_progress_report.pdf"):
                os.remove("user_progress_report.pdf")
            output_file = report_generator.generate_report(prompt, "user_progress_report.pdf")
            
            print(f"{Fore.GREEN}Report exported successfully to {output_file}.{Style.RESET_ALL}")
        except Exception as e:
            print(f"Error exporting report: {str(e)}")

if __name__ == "__main__":
    try:
        simulator = EnglishPracticeSimulator()
        simulator.run()
    except Exception as e:
        print(f"An error occurred while running the simulator: {str(e)}")
