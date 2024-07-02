from colorama import Fore, Style
from .authentication import GoogleAuthenticator
from .utils.json_utils import load_json, save_json

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
            self.counters = {"operations": 0, "max_streak": 0, "current_streak": 0}
            self.achievements = []

    def __load_counters(self):
        """
        Load counter values for the current user.

        Returns:
            dict: A dictionary containing 'operations', 'max_streak', and 'current_streak' counters.
        """
        try:
            user_data = load_json('db/user_stats.json') or {}
            user_stats = user_data.get(self.user_id, {})
            return {
                "operations": user_stats.get("operations", 0),
                "max_streak": user_stats.get("max_streak", 0),
                "current_streak": user_stats.get("current_streak", 0)
            }
        except Exception as e:
            print(f"Error loading counters: {e}")
            return {"operations": 0, "max_streak": 0, "current_streak": 0}

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
                    self.counters["max_streak"] >= int(achievement.get("required_streak", 0)))
            ]
        except Exception as e:
            print(f"Error getting unlocked achievements: {e}")
            return []

    def update_achievements(self):
        """
        Update the user's achievements based on the latest operations count and max streak.
        """
        try:
            self.counters = self.__load_counters()
            self.achievements = self.__get_unlocked_achievements()
        except Exception as e:
            print(f"Error updating achievements: {e}")

    def display_achievements(self, is_for_report: bool = False):
        """
        Display the user's unlocked achievements, current operations count, current streak, and max streak.

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
            print(f"Current streak: {self.counters['current_streak']}")
            print(f"Max streak: {self.counters['max_streak']}")
            print("-------------------")
        else:
            return self.achievements

    def display_all_achievements(self):
        """
        Display all achievements, including locked and unlocked ones.
        """
        print("\n--- All Achievements ---")
        try:
            self.update_achievements()  # Ensure we have the latest data
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
                    if self.counters['operations'] >= required_operations and self.counters['max_streak'] >= required_streak:
                        status = f"{Fore.GREEN}Unlocked{Style.RESET_ALL}"
                
                print(f"- {name} ({status}): {description}")
                print(f"  Required: Operations: {required_operations}, Streak: {required_streak}")
            print(f"  Current: Operations: {self.counters['operations']}, Current Streak: {self.counters['current_streak']}, Max Streak: {self.counters['max_streak']}")
        except Exception as e:
            print(f"Error displaying all achievements: {e}")
        print("------------------------")

    def update_counters(self, operations=0, current_streak=0, max_streak=0):
        """
        Update the user's counters and save them to the JSON file.
        """
        try:
            user_data = load_json('db/user_stats.json') or {}
            user_stats = user_data.get(self.user_id, {})
            
            user_stats['operations'] = user_stats.get('operations', 0) + operations
            user_stats['current_streak'] = current_streak
            user_stats['max_streak'] = max(user_stats.get('max_streak', 0), max_streak)
            
            user_data[self.user_id] = user_stats
            save_json('db/user_stats.json', user_data)
            
            self.counters = self.__load_counters()
            self.update_achievements()  # Update achievements after updating counters
        except Exception as e:
            print(f"Error updating counters: {e}")