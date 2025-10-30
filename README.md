# DDoS Preventer: A Layered DDoS Protection Shield

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

This project is a Python-based transparent proxy designed to protect servers against DDoS (Distributed Denial of Service) attacks. It leverages `iptables` to intercept network traffic, analyzing it across multiple layers (Layer 4 and Layer 7) to block malicious traffic before it reaches your application.

It can be used to protect web servers, game servers, databases, or any other public-facing TCP service without requiring any modifications to your existing application.

## ✨ Features

*   **Transparent Proxy Architecture:** Works with `iptables`, making it invisible to both the client and the server application.
*   **Layer 4 (TCP) Protection:** Applies rate and connection limiting for generic or encrypted TCP services like HTTPS, SSH, and MySQL.
*   **Layer 7 (HTTP) Protection:** Analyzes HTTP traffic for more intelligent mitigation.
*   **Token Bucket Rate Limiting:** Restricts the number of requests per second for each IP address.
*   **Connection Limiting:** Limits the total number of concurrent connections an IP can establish.
*   **Geo-Blocking:** Applies stricter limits to traffic originating from countries not on the trusted list.
*   **Dynamic Blacklisting:** Automatically blocks IPs that exceed the limits for a configurable duration.
*   **Automatic Port Discovery:** Automatically discovers and protects all public-facing ports on the server.

## ⚙️ How It Works

The system acts as a security filter that inspects all incoming traffic before it reaches your services like Nginx.

```
          Internet User
                 |
                 v
[ Server Network Interface (Target: Port 80, 443, etc.) ]
                 |
                 | <--- iptables rule: "Redirect traffic to the Python script!"
                 v
   [ DDoS Preventer Script (Security Filter) ]
   |
   |--> 1. Geo-IP Check
   |--> 2. Blacklist Check
   |--> 3. Rate & Connection Limit Check
   |
   |--(If Threat)--> [ DROP CONNECTION ]
   |
   |--(If Safe)--> [ Forward to original destination (Nginx, etc.) ]
   |
   v
[ Your Application (Nginx, Apache, SSH Server, etc.) ]
```

## 🚀 Installation

**Prerequisites:**
*   A Linux-based operating system (e.g., Debian, Ubuntu, CentOS).
*   Root (`sudo`) privileges.
*   Python 3.8+

**Step 1: Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

**Step 2: Install System Dependencies**
The `iptables` and `ss` commands must be available on your system.

*   For Debian/Ubuntu:
    ```bash
    sudo apt-get update
    sudo apt-get install -y python3-pip iptables iproute2
    ```
*   For CentOS/RHEL:
    ```bash
    sudo yum install -y python3-pip iptables iproute
    ```

**Step 3: Install Python Libraries**
From the project's root directory, install the required libraries using `requirements.txt`.
```bash
pip3 install -r requirements.txt
```

**Step 4: Download the GeoIP Database**
This project uses MaxMind's GeoLite2 database for Geo-blocking.

1.  Create a free account on the [MaxMind signup page](https://www.maxmind.com/en/geolite2/signup).
2.  After logging in, navigate to "Download Databases" from the left-hand menu.
3.  Download the **"GeoLite2 Country"** database in the **"Download GZIP"** format.
4.  Extract the downloaded `GeoLite2-Country_...tar.gz` file.
5.  Move the resulting `GeoLite2-Country.mmdb` file into the `core/` directory of your project.

## 🛠️ Configuration

All settings can be adjusted in the `config.py` file.

*   `TARGET_PORTS`: A base list for ports you want to protect manually (e.g., SSH).
*   `WELL_KNOWN_HTTP_PORTS`: A list of ports that the auto-discovery should classify as 'http'.
*   `DEFAULT_RATE`, `DEFAULT_BURST`: The per-IP requests per second and burst limits.
*   `TRUSTED_COUNTRIES`: A set of country codes (e.g., `'US'`) that will bypass the stricter country-wide rate limits.

## ▶️ Usage

The script must be run with `sudo` as it needs to manipulate `iptables` rules and read low-level socket information.

```bash
sudo python3 main.py
```

When started, the script will automatically discover open ports, set up the `iptables` rules, and begin filtering traffic.

To stop the script, press `Ctrl+C`. It will automatically clean up all `iptables` rules it created, restoring the system to its original state.

## ⚖️ License

This project is licensed under the MIT License. See the `LICENSE` file for details.
