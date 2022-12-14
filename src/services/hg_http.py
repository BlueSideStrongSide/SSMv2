import asyncio
import time
import aiohttp
from src.notifications.pushover.notifications import PushOver as push_notify
from datetime import datetime


# move to **kwargs
class HGHttpServiceMonitor:
    def __init__(self, target,
                 interval=5,
                 count=1,
                 port=None,
                 service=None,
                 _results_tracker=None,
                 _target_options=None,
                 internal_logger=None):
        """
        Class handler for the HTTP service monitor

        :param target: hostname or IP that will be monitored
        :param interval: time between status checks
        :param count:  Currently not used
        :param port: port used for HTTP/HTTPS status checks
        :param service: used to map HTTP or HTTPS options
        :param _results_tracker: Class access to store and retrieve results
        :param internal_logger: Class access to store log files
        """
        self._target = target
        self._target_options = _target_options
        self._port = port or 443
        self._service = service or "HTTP"
        self._interval = interval
        self._timeout = 60
        self._alert_enabled = self._target_options['alert'] or False
        self._failure_counter = int(self._target_options['failure_count'])
        self._privileged = False

        self._internal_logger = internal_logger
        self._http_results_tracker = []
        self._results_tracker = _results_tracker  # <-- Class result to implement later

        self.pushover_notifier = push_notify()

    @property
    def format_url(self):
        return f'{self._service}://{self._target}:{self._port}'

    @property
    def success_char(self):
        return u'\u2705'

    @property
    def fail_char(self):
        return u'\u274C'

    @property
    def dispatch_alert_conditions_met(self):
        if len(self._http_results_tracker) >= self._failure_counter and self._alert_enabled:
            self._http_results_tracker = []
            return True
        return False

    async def get_target(self):
        _internal_count = 0

        async  with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            while True:
                try:
                    latency_check = time.time()
                    async with session.get(self.format_url, timeout=2) as response:

                        # convert latency to seconds
                        duration = (time.time() - latency_check) * 1000
                        self._internal_logger.info(
                            f'{self.success_char} {self.format_url} --> Status:{response.status} --> Duration:{duration:.2f}ms')

                # Limit exception captures
                except Exception as e:
                    error_message = f'{self.fail_char} {self.format_url} --> {e} --> Failed To Connect'

                    self._internal_logger.info(error_message)
                    self._http_results_tracker.append(error_message)

                    if self.dispatch_alert_conditions_met and self._target_options["ALERT"].lower() == "true":
                        await self.pushover_notifier.send_alert(message=error_message)

                _internal_count += 1  # <-- decide if we want to keep this currently not used

                for i in range(1, int(self._interval)):
                    await asyncio.sleep(1)


if __name__ == '__main__':
    target_test = {'target': 'raspberrypi', 'service': 'HTTP', 'port': '3000', 'interval': '30', 'alert': 'TRUE'}
    asyncio.run(HGHttpServiceMonitor(target=target_test['target'], interval=int(target_test['interval']), port=target_test['port'],
                                     service=target_test['service']).get_target())
