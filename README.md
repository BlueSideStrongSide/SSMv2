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
