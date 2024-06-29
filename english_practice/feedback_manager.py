import json
from datetime import datetime
from colorama import Fore, Style
from .authentication import GoogleAuthenticator
from .utils.json_utils import load_json, save_json

class FeedbackManager:
    """
    Manages feedback data for English practice sessions.
    Provides functionality to save and display feedback for individual users.
    """

    def __init__(self, filename: str = "english_practice_feedback.json"):
        """
        Initialize the FeedbackManager with a filename for storing feedback.

        Args:
            filename (str): Name of the file to store feedback data. Defaults to "english_practice_feedback.json".
        """
        self.filename: str = filename
        self.user_id: str = None
        try:
            self.user_id = GoogleAuthenticator().get_stored_user_id()
        except Exception as e:
            print(f"{Fore.RED}Error getting user ID: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Feedback will not be saved.{Style.RESET_ALL}")

    def save_feedback(self, feedback: str) -> None:
        """
        Save the provided feedback to the file for the current user.

        Args:
            feedback (str): The feedback to save.

        Raises:
            IOError: If there's an issue writing to the file.
        """
        if self.user_id is None:
            print(f"{Fore.RED}Error: User ID is None. Cannot save feedback.{Style.RESET_ALL}")
            return

        new_feedback = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feedback": feedback
        }

        try:
            existing_data = load_json(self.filename)
            if not isinstance(existing_data, dict):
                existing_data = {}
            existing_data.setdefault(self.user_id, []).append(new_feedback)
            save_json(self.filename, existing_data)
            print(f"{Fore.GREEN}Feedback saved successfully.{Style.RESET_ALL}")
        except IOError as e:
            print(f"{Fore.RED}Error saving feedback: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Unexpected error occurred while saving feedback: {e}{Style.RESET_ALL}")

    def display_feedbacks(self) -> list:
        """
        Display all feedbacks stored in the file for the current user.

        Returns:
            list: A list of feedback dictionaries for the current user.

        Raises:
            json.JSONDecodeError: If there's an issue parsing the JSON file.
        """
        if self.user_id is None:
            print(f"{Fore.RED}Error: User ID is None. Cannot display feedbacks.{Style.RESET_ALL}")
            return []

        try:
            feedbacks = load_json(self.filename)
            if not isinstance(feedbacks, dict):
                print(f"{Fore.YELLOW}No valid feedback data found.{Style.RESET_ALL}")
                return []
            
            user_feedbacks = feedbacks.get(self.user_id, [])

            print(f"\n{Fore.CYAN}English Practice Feedbacks for User:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")

            if not user_feedbacks:
                print(f"{Fore.YELLOW}No feedbacks found for this user.{Style.RESET_ALL}")
            else:
                for feedback in user_feedbacks:
                    print(f"{Fore.YELLOW}Date: {feedback['timestamp']}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Feedback:{Style.RESET_ALL}")
                    print(f"{feedback['feedback']}")
                    print(f"{Fore.CYAN}{'-' * 80}{Style.RESET_ALL}")
            return user_feedbacks
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Error parsing JSON file: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Unexpected error occurred while displaying feedbacks: {e}{Style.RESET_ALL}")
        return []
