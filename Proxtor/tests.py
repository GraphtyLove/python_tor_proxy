import unittest
from main import Tor


class TestTor(unittest.TestCase):
    def setUp(self):
        self.tor = Tor(tor_password="password", tor_port=9051)

    def test_get_request(self):
        response = self.tor.get_request("http://httpbin.org/ip")
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        response = self.tor.post_request(
            "http://httpbin.org/post", request_body={"key": "value"}
        )
        self.assertEqual(response.status_code, 200)

    def test_get_ip(self):
        ip = self.tor.get_ip(show_tor_ip=True)
        self.assertRegex(ip, r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

    def test_renew_tor_ip(self):
        old_ip = self.tor.get_ip(show_tor_ip=True)
        self.tor.get_new_ip(max_retries=5)
        new_ip = self.tor.get_ip(show_tor_ip=True)
        # This test might fail sometimes if the TOR network gives you the same IP again.
        # However, this should be rare, especially with 5 retries.
        self.assertNotEqual(old_ip, new_ip)


if __name__ == "__main__":
    unittest.main()
