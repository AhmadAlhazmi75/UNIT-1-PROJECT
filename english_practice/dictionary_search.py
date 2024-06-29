from .external_assets import ExternalAssets
from colorama import Fore, Style
import urllib.parse
import asyncio

class DictionarySearch(ExternalAssets):
    """
    This class is used to search the dictionary for a word.
    It inherits from ExternalAssets to utilize the open_in_browser functionality.
    """
    def __init__(self):
        """
        Initialize the DictionarySearch object with an empty URL.
        The URL will be dynamically set when a word is searched.
        """
        super().__init__("Dictionary", "")
        self.word = None

    async def search_dictionary(self):
        """
        Prompt the user for a word, validate the input, and open the dictionary page for that word.
        
        This method performs the following steps:
        1. Prompt the user to enter a word
        2. Validate that the input is a single word and not empty
        3. Update the URL for the dictionary search with proper encoding
        4. Open the dictionary page in the default web browser
        5. Print a confirmation message
        
        If the input is invalid (empty or more than one word), an error message is displayed and the method returns.
        """
        try:
            self.word = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input(f"{Fore.YELLOW}Enter the word you want to search: {Style.RESET_ALL}")
            )
            
            if not self.word or len(self.word.split()) > 1:
                print(f"{Fore.RED}Invalid input. Please enter a single word.{Style.RESET_ALL}")
                return
            
            encoded_word = urllib.parse.quote(self.word)
            self._url = f"https://www.dictionary.com/browse/{encoded_word}"
            
            self.open_in_browser()
            print(f"{Fore.GREEN}Opening dictionary for: {self.word}...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
