from colorama import Fore, Style
from .authentication import GoogleAuthenticator
from .utils.json_utils import load_json

class Achievements:
    """
    A class to manage user achievements based on operation counts and streaks.
    """

    def __init__(self):
        """
        Initialize the Achievements object.
        """
        try:
            self.user_id = GoogleAuthenticator().get_stored_user_id()
            self.all_achievements = load_json('achievement.json')
            self.operations_count = self.__load_counter('operations_counter.json', "operations")
            self.streak_count = self.__load_counter('streak_counter.json', "streak")
            self.achievements = self.__get_unlocked_achievements()
        except Exception as e:
            print(f"Error initializing Achievements: {e}")
            self.user_id = None
            self.all_achievements = {}
            self.operations_count = 0
            self.streak_count = 0
            self.achievements = []

    def __load_counter(self, filename, key):
        """
        Load a counter value for the current user.

        Args:
            filename (str): The JSON file to load from.
            key (str): The key for the counter in the JSON data.

        Returns:
            int: The counter value for the user.
        """
        try:
            data = load_json(filename)
            return data.get(self.user_id, {}).get(key, 0)
        except Exception as e:
            print(f"Error loading counter from {filename}: {e}")
            return 0

    def __get_unlocked_achievements(self):
        """
        Get the list of unlocked achievements for the user.

        Returns:
            list: A list of unlocked achievements.
        """
        try:
            return [
                achievement for achievement in self.all_achievements.get("achievements", [])
                if (self.operations_count >= int(achievement.get("required_operations", 0)) and 
                    self.streak_count >= int(achievement.get("required_streak", 0)))
            ]
        except Exception as e:
            print(f"Error getting unlocked achievements: {e}")
            return []

    def load_streak_count(self):
        """
        Load the streak count for the current user.

        Returns:
            int: The streak count for the user.
        """
        return self.__load_counter('streak_counter.json', "streak")

    def update_achievements(self):
        """
        Update the user's achievements based on the latest operations count and streak.
        """
        try:
            self.operations_count = self.__load_counter('operations_counter.json', "operations")
            self.streak_count = self.load_streak_count()
            self.achievements = self.__get_unlocked_achievements()
        except Exception as e:
            print(f"Error updating achievements: {e}")

    def display_achievements(self):
        """
        Display the user's unlocked achievements, current operations count, and streak.

        Returns:
            list: The list of unlocked achievements.
        """
        print("\n--- Achievements ---")
        if not self.achievements:
            print("No achievements unlocked yet.")
        else:
            print("Unlocked Achievements:")
            for achievement in self.achievements:
                print(f"- {achievement['name']}: {achievement['description']}")
        print(f"\nCurrent operations count: {self.operations_count}")
        print(f"Current streak: {self.streak_count}")
        print("-------------------")
        return self.achievements

    def display_all_achievements(self):
        """
        Display all achievements, including locked and unlocked ones.
        """
        print("\n--- All Achievements ---")
        try:
            unlocked = set(achievement['name'] for achievement in self.achievements)
            for achievement in self.all_achievements["achievements"]:
                status = f"{Fore.GREEN}Unlocked{Style.RESET_ALL}" if achievement['name'] in unlocked else f"{Fore.RED}Locked{Style.RESET_ALL}"
                print(f"- {achievement['name']} ({status}): {achievement['description']}")
        except Exception as e:
            print(f"Error displaying all achievements: {e}")
        print("------------------------")
