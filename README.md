# Proxtor
Proxtor is a Python library that allows you to send HTTP requests over the TOR network. 
It simplifies interacting with TOR and helps with IP renewal, sending GET/POST requests, and more.

## Installation
Proxtor can be installed using pip:

```bash
pip install Proxtor
```

## Requirements
Proxtor requires Tor to be installed on your machine and running.
It also assumes that the Tor control port is set to 9051 and that the password is set to 'your_password' 
(the password and port can be changed when initializing Proxtor).

The package as been written in python3.11 but should work with any version of python 3.7+.

A Docker image is available [here](https://hub.docker.com/r/dperson/Proxtor/).

If you want to do something more custom, an example Dockerfile is available in the repository.

## Usage
### Initialization
Proxtor is very easy to use. Here is an example of how to use it:

```python
from Proxtor import Tor
tor = Tor(tor_password='your_password', tor_port=9051)

# Get request
response = tor.get_request(url='https://example.com', headers={'User-Agent': 'Mozilla/5.0'})
print(response.content)

# Post request
response = tor.post_request(url='https://example.com', headers={'User-Agent': 'Mozilla/5.0'}, data={'key': 'value'})
print(response.content)

# Get the current IP
# Tor ip
print(tor.get_ip())
# Local machine ip
print(tor.get_ip(show_tor_ip=False))

# Get a new IP (won't work 100% of the time as it depends on the exit node)
tor.get_new_ip(max_retries=5)
```

## Logging
Logging is enabled by default, with the log level set to INFO. 
You will find logs for key events such as TOR IP renewal failures.

## Contributing
Contributions are very welcome. 
Please submit a pull request or create an issue for any enhancements, bugs or feature requests.

## License
This project is licensed under the MIT license. See the [LICENSE](./LICENSE) file for details.