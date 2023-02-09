import asyncio
import time
import aiohttp
import json
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

        # service options
        self._target = target
        self._target_options = _target_options
        self._interval = interval
        self._service = service or "HTTP"
        self._port = port or 443
        self._timeout = 60

        # configuration options
        self._alert_enabled = self._target_options['alert'] or False
        self._ms_check = self._target_options.get('ms_check') or False
        self._failure_counter = int(self._target_options['failure_count'])
        self._ms_calc = str(self._target_options.get('ms_calc')).lower() or "gt"
        self._ms_value = int(self._target_options.get('ms_value', 0))
        self._expected_response = self._target_options.get('expected_response_text')

        self._internal_logger = internal_logger
        self._http_results_run_tracker = {"success": [], "fail": []}
        self._http_results_fail_tracker = []
        self._results_tracker = _results_tracker  # <-- Class result to implement later

        self.pushover_notifier = push_notify()

        self._internal_logger.debug(self.__class__)

    @property
    def format_url(self, wan_monitor: str = "https://api.ipify.org"):
        if self._service == "WAN":
            return wan_monitor
        return f'{self._service}://{self._target}:{self._port}'

    @property
    def success_char(self):
        return u'\u2705'

    @property
    def fail_char(self):
        return u'\u274C'

    @property
    def dispatch_alert_conditions_met(self, immediate: bool = False):
        self._internal_logger.debug("Checking if alert conditions are met")
        if (len(self._http_results_run_tracker["fail"]) >= self._failure_counter) and self._alert_enabled:
            self._failure_counter = self._failure_counter + int(self._target_options['failure_count'])
            return True
        return False

    async def get_target(self):
        _internal_count = 0

        self._internal_logger.debug(f'Starting AIOHTTP session for {self.format_url} ')

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            while True:
                try:
                    latency_check = time.time()

                    async with session.get(self.format_url, timeout=2) as response:

                        api_response = await response.text()

                        # convert latency to seconds
                        duration = (time.time() - latency_check) * 1000

                        status_message = f'{self.success_char} {self.format_url} --> Status:{response.status} --> Service:{self._service} --> Duration:{duration:.2f}ms'

                        self._http_results_run_tracker["success"].append({"url": self.format_url,
                                                                          "status_code": response.status,
                                                                          "duration": duration,
                                                                          "duration_normalized": int(duration),
                                                                          })
                        self._internal_logger.info(status_message)

                # Limit exception captures
                except Exception as e:

                    error_message = f'{self.fail_char} {self.format_url} --> {e} --> Failed To Connect'
                    self._internal_logger.info(error_message)

                    await asyncio.sleep(0)

                    self._http_results_run_tracker["fail"].append({"url": self.format_url,
                                                                   "status": error_message,
                                                                   "specific_error": e
                                                                   })

                    if self.dispatch_alert_conditions_met:
                        await self.pushover_notifier.send_alert(message=error_message)

                # latency check v1 currently as conditions are met they will be dispatched
                if self._ms_check:
                    self._internal_logger.debug(f'Starting ms_check function for {self.format_url}')

                    await self.check_latency(duration)

                # latency check v1 currently as conditions are met they will be dispatched
                if self._service == "WAN":
                    self._internal_logger.debug(f'Starting WAN monitor function for {self.format_url}')

                    await self.check_wan(api_response)

                _internal_count += 1  # <-- decide if we want to keep this currently not used

                self._internal_logger.debug(f'Starting interval sleep for {self.format_url}')
                for i in range(1, int(self._interval)):
                    await asyncio.sleep(1)

    async def check_wan(self, response):
        if self._expected_response == response:
            return True
        else:
            error_message = f'The expected WAN address {self._expected_response} does not match what was returned {response}'
            self._http_results_run_tracker["fail"].append({"url": self.format_url,
                                                           "status": error_message,
                                                           })

            self._internal_logger.info(error_message)  # <-- this can probably get removed

            if self.dispatch_alert_conditions_met:
                await self.pushover_notifier.send_alert(message=error_message)

        self._internal_logger.debug(f'finish check_wan function')

    async def check_latency(self, duration):
        if self._ms_check:
            error_message = ""

            # average over the last 10 items processed
            if self._ms_calc == 'avg' and len(self._http_results_run_tracker["success"]) >= 3:
                self._internal_logger.debug(f'checking if provided latency is {self._ms_calc} --> {self._ms_value}')

                # get the most recent three items this will be dynamic later
                recent_items = self._http_results_run_tracker["success"][-3:]
                calculated_latency = [latency["duration_normalized"] for latency in recent_items]

                latency_average = sum(calculated_latency) // len(calculated_latency)

                if latency_average > self._ms_value:
                    error_message = f'{self.fail_char} {self.format_url} --> {duration:.2f} --> observed latency average higher than expected {self._ms_value}'

            # specified value is less than returned
            if self._ms_calc == 'lt' and self._ms_value > int(duration):
                self._internal_logger.debug(f'checking if provided latency is {self._ms_calc} --> {self._ms_value}')
                error_message = f'{self.fail_char} {self.format_url} --> {duration:.2f} --> observed latency lower than expected {self._ms_value}'

            # specified value is greater than returned
            if self._ms_calc == 'gt' and (self._ms_value < int(duration)):
                self._internal_logger.debug(f'checking if provided latency is {self._ms_calc} --> {self._ms_value}')
                error_message = f'{self.fail_char} {self.format_url} --> Duration: {duration:.2f} observed latency higher than expected value --> {self._ms_value}'

            if error_message:
                self._internal_logger.info(error_message)
                await asyncio.sleep(0)
                await self.pushover_notifier.send_alert(message=error_message)

            self._internal_logger.debug(f'finished ms_latency check for {self.format_url}')


if __name__ == '__main__':
    target_test = {'target': 'raspberrypi', 'service': 'HTTP', 'port': '3000', 'interval': '30', 'alert': 'TRUE'}
    asyncio.run(HGHttpServiceMonitor(target=target_test['target'], interval=int(target_test['interval']),
                                     port=target_test['port'],
                                     service=target_test['service']).get_target())
