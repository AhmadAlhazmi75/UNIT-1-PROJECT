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
            self.all_achievements = load_json('db/achievement.json') or {}
            self.counters = self.__load_counters()
            self.achievements = self.__get_unlocked_achievements()
        except Exception as e:
            print(f"Error initializing Achievements: {e}")
            self.user_id = None
            self.all_achievements = {}
            self.counters = {"operations": 0, "streak": 0}
            self.achievements = []

    def __load_counters(self):
        """
        Load counter values for the current user.

        Returns:
            dict: A dictionary containing 'operations' and 'streak' counters.
        """
        try:
            operations_data = load_json('db/operations_counter.json') or {}
            streak_data = load_json('db/streak_counter.json') or {}
            return {
                "operations": operations_data.get(self.user_id, {}).get("operations", 0),
                "streak": streak_data.get(self.user_id, {}).get("streak", 0)
            }
        except Exception as e:
            print(f"Error loading counters: {e}")
            return {"operations": 0, "streak": 0}

    def __get_unlocked_achievements(self):
        """
        Get the list of unlocked achievements for the user.

        Returns:
            list: A list of unlocked achievements.
        """
        try:
            return [
                achievement for achievement in self.all_achievements.get("achievements", [])
                if (self.counters["operations"] >= int(achievement.get("required_operations", 0)) and 
                    self.counters["streak"] >= int(achievement.get("required_streak", 0)))
            ]
        except Exception as e:
            print(f"Error getting unlocked achievements: {e}")
            return []

    def update_achievements(self):
        """
        Update the user's achievements based on the latest operations count and streak.
        """
        try:
            self.counters = self.__load_counters()
            self.achievements = self.__get_unlocked_achievements()
        except Exception as e:
            print(f"Error updating achievements: {e}")

    def display_achievements(self, is_for_report: bool = False):
        """
        Display the user's unlocked achievements, current operations count, and streak.

        Returns:
            list: The list of unlocked achievements.
        """
        if not is_for_report:
            print("\n--- Achievements ---")
            if not self.achievements:
                print("No achievements unlocked yet.")
            else:
                print("Unlocked Achievements:")
                for achievement in self.achievements:
                    print(f"- {achievement['name']}: {achievement['description']}")
            print(f"\nCurrent operations count: {self.counters['operations']}")
            print(f"Current streak: {self.counters['streak']}")
            print("-------------------")
        else:
            return self.achievements

    def display_all_achievements(self):
        """
        Display all achievements, including locked and unlocked ones.
        """
        print("\n--- All Achievements ---")
        try:
            unlocked = set(achievement.get('name', '') for achievement in self.achievements)
            for achievement in self.all_achievements.get("achievements", []):
                name = achievement.get('name', 'Unknown')
                description = achievement.get('description', 'No description available')
                required_operations = achievement.get('required_operations', 0)
                required_streak = achievement.get('required_streak', 0)
                
                if name in unlocked:
                    status = f"{Fore.GREEN}Unlocked{Style.RESET_ALL}"
                else:
                    status = f"{Fore.RED}Locked{Style.RESET_ALL}"
                    if self.counters['operations'] >= required_operations and self.counters['streak'] >= required_streak:
                        status = f"{Fore.GREEN}Unlocked{Style.RESET_ALL}"
                
                print(f"- {name} ({status}): {description}")
            print(f"  Current: Operations: {self.counters['operations']}, Streak: {self.counters['streak']}")
        except Exception as e:
            print(f"Error displaying all achievements: {e}")
        print("------------------------")
