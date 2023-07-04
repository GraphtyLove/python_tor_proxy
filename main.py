"""
Module for TOR network interaction via Python requests.
"""

from typing import Dict, Any, Optional, List
import requests
import os
import time
import logging
from stem import Signal
from stem.control import Controller

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tor:
    """
    Class to handle interactions with the TOR network.

    The class is initialized with a TOR password and port, as well as optional headers for requests.
    :param tor_password: The TOR password, defaults to environmental variable or placeholder.
    :param tor_port: The TOR port, defaults to 9050.
    :param headers: Optional dictionary of headers.

    Attributes:
        _proxies (dict): Dictionary containing the HTTP and HTTPS proxies.
        _tor_password (str): The password to access the TOR controller.
        headers (dict): Optional headers for requests.
        _controller (stem.control.Controller): The TOR controller.
        _session (requests.Session): Session object for making requests.
        ip_history (list): A history of previous IPs used in the TOR network.
    """

    _get_ip_url = (
        "https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data"
    )

    def __init__(
        self,
        tor_password: str = os.environ.get("TOR_PASSWORD", "YOUR_PASSWORD_HERE"),
        tor_port: int = 9050,
        headers: Optional[Dict[str, str]] = None,
    ):
        # Initialize TOR
        os.system("service tor start")

        self._proxies = {
            "http": f"socks5h://127.0.0.1:{tor_port}",
            "https": f"socks5h://127.0.0.1:{tor_port}",
        }
        self._tor_password = tor_password
        self.headers = headers if headers is not None else {}
        self._controller = Controller.from_port(port=9051)
        self._session = requests.Session()
        self._session.proxies = self._proxies
        self._session.headers = self.headers  # type: ignore

        self.ip_history: List[str] = []

    def _merge_headers(self, new_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Merges base and request-specific headers.

        :param new_headers: Dictionary of headers to merge with the base headers.
        :return: Merged headers dictionary.
        """
        if new_headers is None:
            return self.headers
        else:
            new_headers.update(self.headers)
            return new_headers

    def _close_all_circuits(self) -> None:
        """Closes all circuits to ensure usage of new IP after renewal."""

    def get_new_ip(self, max_retries=5) -> None:
        """
        Attempts to renew TOR IP up to maximum retries.

        :param max_retries: Maximum number of IP renewal attempts, defaults to 5.
        """
        for _ in range(max_retries):
            tor_current_ip = self.get_ip()
            self.ip_history.append(tor_current_ip)
            self._controller.authenticate(password=self._tor_password)
            self._controller.signal(Signal.NEWNYM)
            time.sleep(self._controller.get_newnym_wait())
            self._close_all_circuits()
            new_ip = self.get_ip()
            if new_ip != tor_current_ip:
                return
            logger.info("Renewing IP failed, retrying...")
        logger.error(f"Failed to renew IP after {max_retries} retries.")

    def get_request(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Sends a GET request via TOR.

        :param url: URL to send the GET request to.
        :param headers: Optional headers for the request.
        :return: Server response.
        """
        headers = self._merge_headers(headers)
        response = self._session.get(url, proxies=self._proxies, headers=headers)
        return response

    def post_request(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        request_body: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Sends a POST request via TOR.

        :param url: URL to send the POST request to.
        :param headers: Optional headers for the request.
        :param request_body: Optional JSON request body.
        :return: Server response.
        """
        headers = self._merge_headers(headers)
        response = self._session.post(
            url,
            proxies=self._proxies,
            headers=headers,
            json=request_body if request_body is not None else {},
        )
        return response

    def get_ip(self, show_tor_ip: bool = True) -> str:
        """
        Returns current IP, either local or TOR.

        :param tor_ip: If True, return the TOR IP, else return the local IP.
        :return: Current IP as a string.
        """
        local_ip = requests.get(self._get_ip_url).json().get("ip", "")

        if show_tor_ip:
            tor_ip = self.get_request(self._get_ip_url).json().get("ip")
            if local_ip == tor_ip:
                logger.error("Your IP is not protected!")
            return tor_ip
        else:
            return local_ip
