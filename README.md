**Proxy Server README**

This README provides an overview and usage guide for the provided Python Proxy Server script. The Proxy Server is designed to intercept and forward HTTP requests and responses between clients and remote servers while offering additional features like caching, whitelisting, and time-based access control.

## Project Structure

- `main.py`: Main script to run the proxy server and GUI concurrently.
- `GUI/`: Directory containing GUI-related files.
  - `ProxyGUI.py`: Implementation of the GUI using Tkinter.
- `Proxy/`: Directory containing proxy-related files.
  - `ProxyModule.py`: Implementation of the proxy server.
  - `config.txt`: Configuration file for the proxy server.
  - `Forbidden.html`: HTML file for forbidden response content.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Supported Use Cases](#supported-use-cases)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [License](#license)

## Features

1. **HTTP Proxy Server**: The script acts as an intermediary between clients and remote servers, forwarding HTTP requests and responses.

2. **Caching**: The server can cache response data from remote servers to optimize subsequent requests for the same resources.

3. **Whitelisting**: Only requests to whitelisted domains will be processed; others will be rejected.

4. **Time-Based Access Control**: Access to the proxy can be restricted based on a specified time window.

5. **Support for GET, POST, HEAD Methods**: The server handles these common HTTP methods.

6. **Dynamic Handling**: The server dynamically handles requests according to the method provided.
7. **Multithreading**: Handling multiple client requests simultaneously.

## Prerequisites

- Python 3.x

## Configuration

The behavior of the Proxy Server can be configured using the `config.txt` file. Modify the following options:

- `cache_time`: The time (in seconds) to keep cached responses.
- `whitelisting`: Comma-separated list of whitelisted domains.
- `time`: Comma-separated time window during which the proxy is allowed to operate.

## Usage

1. Ensure that the `config.txt` file is configured properly with your desired settings.
   ```
   cache_time=900 // seconds
   whitelisting=oosc.online, example.com, vbsca.ca, testphp.vulnweb.com // domain name
   time=8-24 // time allowed access
   ```

3. Run the Proxy Server script by executing the following command in your terminal:

   ```
   python proxy_server.py
   ```

4. The Proxy Server will start listening on the specified host and port (default is `127.0.0.1:8888`).

## Supported Use Cases

The Proxy Server can be used to:

- Intercept and analyze HTTP traffic.
- Test caching mechanisms.
- Control access to specific websites.
- Implement time-based access control.
- Learn about proxy server architecture and implementation.

## Known Limitations

- The Proxy Server only supports HTTP traffic.
- The server's security aspects are limited and should not be used in production environments without thorough hardening.

## Contributing

Contributions are welcome! If you find issues, have suggestions for improvements, or want to add features, feel free to create pull requests.

## License

The Proxy Server script is released under the [MIT License](LICENSE). You can use, modify, and distribute it freely. However, remember that the server has known limitations, and you should use it responsibly and avoid deploying it in production environments without appropriate security measures.