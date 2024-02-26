## HGServiceMonitor

### Overview

`HGServiceMonitor` is a Python script designed to monitor specified targets based on configurations provided in a configuration file. It supports monitoring services using ICMP (ping) and HTTP/HTTPS protocols. The script logs monitoring results, sends alerts, and provides a flexible framework for extending monitoring capabilities.

### Features

- **Target Configuration:** Specify targets and monitoring parameters in a configuration file (config/targets/targets.ini by default).
- **Logging:** Logs monitoring activities to both console and a log file (/logs/hg_logmonitor.log by default).
- **Service Monitors:** Currently supports ICMP (ping) and HTTP/HTTPS service monitors.
- **Notifications:** Supports sending notifications using Pushover.

### Notifiers

A table of the currently supported notifiers is shown below. Generate the appropriate API settings and add them to the configuration file.

| API      | API Settings                    | Supported |
|----------|---------------------------------|:---------:|
| Pushover | https://pushover.net/apps/build |     ✅     |


### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/your_repository.git
   cd your_repository
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Docker Installation

1. Build Docker image:

   ```bash
   sudo docker build -t ssmv2 .
   ```

2. Run Docker container:

   ```bash
   sudo docker run -dt ssmv2 --restart unless-stopped
   ```

### Configuration

- **Target Configuration File:** Specify the full path to the configuration file using the targets_config parameter in the constructor. The default path is config/targets/targets.ini.
- **Log File:** Specify the full path to the output log file using the output_log parameter in the constructor. The default path is /logs/hg_logmonitor.log.
- **Notification Status:** Control whether notifications are sent during startup by setting the notify_status parameter in the constructor.

# Configuration Definitions

## Target Specification
- **[IP|Hostname]:** Corresponds to the target server, ignored if using LOCAL_WAN service.

## Monitoring Settings
- **SERVICE:** Supported services for monitoring (HTTP|HTTPS|ICMP|WAN).
- **MS_CHECK:** Check for latency/duration values.
- **MS_VALUE:** Value of latency to compare the response.
- **MS_CALC:** Calculation method (AVG|GT|LT).
- **INTERVAL:** Time between requests to the target.
- **ALERT:** Send alerts to the specified service.
- **ALERT_SERVICE:** Supported services for alerts (e.g., Pushover).
- **FAILURE_COUNT:** Number of failures before triggering an alert.
- **EXPECTED_RESPONSE_TEXT:** Compare the text response for HTTP|HTTPS|WAN services.
- **ALERT_THROTTLE:** Currently not implemented.
- **EXPECTED_STATUS_CODE:** Currently not implemented.

### Example Configuration:

```ini
[LOCAL_WAN]
SERVICE = WAN
INTERVAL = 5
ALERT = TRUE
EXPECTED_STATUS_CODE = 200
EXPECTED_RESPONSE_TEXT = WAN_IP_HERE
ALERT_SERVICE = PUSHOVER
FAILURE_COUNT = 5

[192.168.1.1]
SERVICE = HTTPS
MS_CHECK = TRUE
MS_VALUE = 100
MS_CALC = AVG
INTERVAL = 5
ALERT = FALSE
ALERT_SERVICE = PUSHOVER
FAILURE_COUNT = 10

[google.org]
SERVICE = HTTPS
MS_CHECK = TRUE
MS_VALUE = 800
MS_CALC = AVG
INTERVAL = 60
ALERT = TRUE
EXPECTED_STATUS_CODE = 200
ALERT_SERVICE = PUSHOVER
FAILURE_COUNT = 3
```
### Usage

```python
from hg_service_monitor import HGServiceMonitor

### Create an instance of HGServiceMonitor
monitor = HGServiceMonitor()

### Enable the service monitor
monitor.enable_service_monitor()
```

### Dependencies
Python 3.8 or higher
Required Python packages specified in requirements.txt
Contributing
Fork the repository.
Create a new branch.
Make your changes.
Test your changes.
Submit a pull request.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments
The script uses the Pushover library for notifications.
Feel free to contribute, report issues, or suggest improvements!
