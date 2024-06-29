from english_practice.simulator import EnglishPracticeSimulator
from english_practice.authentication import GoogleAuthenticator
from colorama import Fore, Style
import os
import google.auth.exceptions


def main():
    authenticator = None
    
    if not os.path.exists("token.json"):    
        input(f"{Fore.BLUE}Welcome to English Practice Simulator. First, you need to authenticate. Press Enter to continue.{Style.RESET_ALL}")
        authenticator = GoogleAuthenticator()
    else:
        authenticator = GoogleAuthenticator()

    try:
        if authenticator and authenticator.authenticate():
            simulator = EnglishPracticeSimulator()
            simulator.run()
        else:
            print("Authentication failed. Please try again.")
    except google.auth.exceptions.InvalidValue as e:
        print(f"Authentication error: {e}")
        print("Please ensure you have a valid token or try re-authenticating.")

if __name__ == "__main__":
    main()
