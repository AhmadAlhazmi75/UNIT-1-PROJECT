import random
import json
from datetime import datetime
from colorama import Fore, Style
from simple_term_menu import TerminalMenu
from .achievements import Achievements
from .authentication import GoogleAuthenticator
from .utils.json_utils import load_json, save_json

class VocabularyBuilder:
    """
    A class to manage vocabulary quizzes and track user progress.
    """
    def __init__(self):
        """
        Initialize the VocabularyBuilder with necessary attributes and load data.
        """
        try:
            self.user_id = GoogleAuthenticator().get_stored_user_id()
            self.vocabulary_quiz = self.__load_vocabulary()
            self.vocabulary_quiz_reversed = {definition: word for word, definition in self.vocabulary_quiz.items()}
            self.correct_answers = 0
            self.achievements = Achievements()
            self.counters = self.achievements.counters
        except Exception as e:
            print(f"{Fore.RED}Error initializing VocabularyBuilder: {str(e)}{Style.RESET_ALL}")
    
    # Data loading methods
    def __load_vocabulary(self):
        try:
            return load_json('db/vocabulary.json')
        except Exception as e:
            print(f"{Fore.RED}Error loading vocabulary: {str(e)}{Style.RESET_ALL}")
            return {}
    
    def __load_vocabulary_quiz_history(self):
        filename = 'db/vocabulary_quiz_history.json'
        try:
            with open(filename, 'r') as file:
                history = json.load(file)
                return history.get(self.user_id, []) if isinstance(history, dict) else []
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Vocabulary quiz history file not found. Creating a new one.{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}Error loading vocabulary quiz history: {str(e)}{Style.RESET_ALL}")
            return []
    
    # Data saving methods
    def __save_vocabulary_quiz(self):
        if not self.vocabulary_quiz:
            return
        filename = 'db/vocabulary_quiz_history.json'
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_result = {
            "timestamp": current_time,
            "result": f"{self.correct_answers} out of 5"
        }
        try:
            with open(filename, 'r') as file:
                history = json.load(file)
        except FileNotFoundError:
            history = {}
        except Exception as e:
            print(f"{Fore.RED}Error reading vocabulary quiz history: {str(e)}{Style.RESET_ALL}")
            history = {}
        
        if self.user_id not in history:
            history[self.user_id] = []
        
        history[self.user_id].append(new_result)
        
        try:
            with open(filename, 'w') as file:
                json.dump(history, file, indent=4)
        except Exception as e:
            print(f"{Fore.RED}Error saving vocabulary quiz history: {str(e)}{Style.RESET_ALL}")

    # Quiz generation and management
    def generate_quiz(self):
        """
        Generate and conduct a vocabulary quiz with 5 multiple-choice questions.
        """
        try:
            quiz_questions = random.sample(list(self.vocabulary_quiz_reversed.items()), 5)
            self.correct_answers = 0
            
            for question, correct_answer in quiz_questions:
                options = [correct_answer]
                while len(options) < 4:
                    random_word = random.choice(list(self.vocabulary_quiz.keys()))
                    if random_word not in options:
                        options.append(random_word)
                random.shuffle(options)
                
                print(f"{Fore.CYAN}{question}")
                
                menu = TerminalMenu(options, title="Choose the correct answer:")
                selected_index = menu.show()
                
                user_choice = options[selected_index]
                if user_choice.lower() == correct_answer.lower():
                    self.__handle_correct_answer()
                else:
                    self.__handle_incorrect_answer(correct_answer)
            
            self.__display_quiz_results()
            self.__save_quiz_data()
        except Exception as e:
            print(f"{Fore.RED}Error generating quiz: {str(e)}{Style.RESET_ALL}")
        
    def __handle_correct_answer(self):
        self.correct_answers += 1
        self.counters["operations"] += 1
        self.counters["current_streak"] += 1
        self.counters["max_streak"] = max(self.counters["max_streak"], self.counters["current_streak"])
        print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
        
    def __handle_incorrect_answer(self, correct_answer):
        self.counters["current_streak"] = 0
        print(f"{Fore.RED}Sorry, the correct answer is {Fore.GREEN}{correct_answer}{Style.RESET_ALL}.")
        
    def __display_quiz_results(self):
        print(f"\n{Fore.MAGENTA}You got {self.correct_answers} correct answers out of 5 questions.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'Keep trying!' if self.correct_answers < 5 else 'Excellent job!'}{Style.RESET_ALL}")
        
    def __save_quiz_data(self):
        self.__save_vocabulary_quiz()
        self.achievements.update_counters(
            operations=self.correct_answers,
            current_streak=self.counters["current_streak"],
            max_streak=self.counters["max_streak"]
        )
        self.achievements.update_achievements()
    
    # Results display
    def display_vocabulary_quiz_results(self, is_for_report: bool = False):
        """
        Display the vocabulary quiz results for the current user.
        """
        user_history = self.__load_vocabulary_quiz_history()

        if not is_for_report:
            try:
                if not user_history:
                    print(f"{Fore.YELLOW}No vocabulary quiz results available for this user yet.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}Vocabulary quiz results history for current user:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'Date':<20}{'Result':<20}{Style.RESET_ALL}")
                    print("-" * 40)
                    for quiz in user_history:
                        print(f"{Fore.YELLOW}{quiz['timestamp']:<20}{Style.RESET_ALL}{quiz['result']:<20}")
                
                self.__display_statistics()
                self.achievements.display_achievements()
                
                return user_history
            except Exception as e:
                print(f"{Fore.RED}Error displaying vocabulary quiz results: {str(e)}{Style.RESET_ALL}")
                return []
        else:
            return user_history
        
    def __display_statistics(self):
        print(f"\n{Fore.CYAN}Total correct answers: {self.counters['operations']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Current streak: {self.counters['current_streak']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Max correct answers streak: {self.counters['max_streak']}{Style.RESET_ALL}")
