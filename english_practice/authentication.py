import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from .utils.json_utils import load_json, save_json

class GoogleAuthenticator:
    """
    A class to handle Google authentication for the application.
    """

    def __init__(self):
        """
        Initialize the GoogleAuthenticator.
        """
        self.credentials = None
        self.user_id = None

    def authenticate(self):
        """
        Authenticate the user with Google.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        self.__load_or_refresh_credentials()
        
        if self.credentials and self.credentials.valid:
            self.user_id = self.__extract_user_id()
            self.__store_user_id(self.user_id)
            return True
        
        return False

    def __load_or_refresh_credentials(self):
        """
        Load existing credentials or authenticate with Google if necessary.
        """
        if os.path.exists('token.json'):
            self.credentials = Credentials.from_authorized_user_file('token.json')
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                except:
                    self.credentials = None
            elif not self.credentials or not self.credentials.valid:
                self.credentials = None
        
        if not self.credentials:
            self.credentials = self.__authenticate_with_google()

    def __authenticate_with_google(self):
        """
        Perform the Google authentication flow.

        Returns:
            Credentials: The obtained Google credentials.
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            './client_secrets.json',
            scopes=['https://www.googleapis.com/auth/userinfo.email', 'openid']
        )
        credentials = flow.run_local_server(port=8080)
        
        self.__save_credentials(credentials)
        
        return credentials

    def __save_credentials(self, credentials):
        """
        Save the credentials for future use.

        Args:
            credentials (Credentials): The credentials to save.
        """
        try:
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())
        except IOError:
            print("Unable to save credentials. Continuing without saving.")

    def __extract_user_id(self):
        """
        Extract the user ID from the Google ID token.

        Returns:
            str: The unique user identifier.
        """
        id_info = id_token.verify_oauth2_token(
            self.credentials.id_token, 
            Request(), 
            audience=self.credentials.client_id
        )
        return id_info['sub']

    def __store_user_id(self, user_id):
        """
        Store the user ID in a file.

        Args:
            user_id (str): The user ID to store.
        """
        try:
            save_json('user_id.json', {'user_id': user_id})
        except IOError:
            print("Unable to store user ID. Continuing without saving.")

    def get_stored_user_id(self):
        """
        Retrieve the stored user ID from the file.

        Returns:
            str: The stored user ID, or None if not found.
        """
        try:
            data = load_json('user_id.json')
            return data.get('user_id')
        except IOError:
            return None

    def logout(self):
        """
        Log out the user by removing the token file and resetting credentials.
        """
        if os.path.exists('token.json'):
            try:
                os.remove('token.json')
            except IOError:
                print("Unable to remove token file. Please delete it manually.")
        if os.path.exists('user_id.json'):
            try:
                os.remove('user_id.json')
            except IOError:
                print("Unable to remove user ID file. Please delete it manually.")
        self.credentials = None
        self.user_id = None
