import webbrowser

class ExternalAssets:
    """
    This class represents external assets that can be opened in a web browser.

    Attributes:
        _asset_name (str): The name of the asset (protected attribute).
        _url (str): The URL of the asset (protected attribute).
    """

    def __init__(self, asset_name: str, url: str):
        """
        Initialize an ExternalAssets object.

        Args:
            asset_name (str): The name of the asset.
            url (str): The URL of the asset.
        """
        self._asset_name: str = asset_name
        self._url: str = url

    def open_in_browser(self) -> None:
        """
        Open the asset's URL in the default web browser.
        """
        try:
            webbrowser.open(self._url)
        except Exception as e:
            print(f"Error opening URL in browser: {e}")

    def __str__(self) -> str:
        """
        Return a string representation of the ExternalAssets object.

        Returns:
            str: A string containing the asset name and URL.
        """
        return f"The asset {self._asset_name}: {self._url}"
