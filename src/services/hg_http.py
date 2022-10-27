import asyncio
import time
import aiohttp
from src.notifications.pushover.notifications import PUSHOVER as pushover_notifications
from datetime import datetime



class HGHttpServiceMonitor:
    def __init__(self, target, interval=5, count=1, port=None, service=None, _results_tracker=None, internal_logger=None):
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
        self._port = port or 443
        self._service = service or "HTTP"
        self._interval = interval
        self._count = count
        self._timeout = 60
        self._privileged = False
        self._results_tracker = _results_tracker
        self._internal_logger = internal_logger
        self.pushover_notifier = pushover_notifications()

    @property
    def format_url(self):
        return f'{self._service}://{self._target}:{self._port}'

    @property
    def success_char(self):
        return u'\u2705'

    @property
    def fail_char(self):
        return u'\u274C'

    async def get_target(self):
        _internal_count = 0

        async  with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            while True:
                try:
                    latency_check = time.time()
                    async with session.get(self.format_url) as response:
                        duration = (time.time() - latency_check) * 1000
                        self._internal_logger.info(f'{self.success_char} {self.format_url} --> Status:{response.status} --> Duration:{duration:.2f}ms')

                # Limit exception captures
                except Exception as e:
                    error_message = f'{self.fail_char} {self.format_url} --> {e} --> Failed To Connect'
                    self._internal_logger.info(error_message)
                    await self.pushover_notifier._send_alert(message=error_message)

                _internal_count += 1
                await asyncio.sleep(self._interval)


    async def is_alive(address):
        host = await async_ping(address, count=10, interval=0.2)
        print(host)

if __name__ == '__main__':
    target= {'target': 'raspberrypi', 'service': 'HTTP', 'port': '3000', 'interval': '30', 'alert': 'TRUE'}
    asyncio.run(HGHttpServiceMonitor(target=target['target'], interval=int(target['interval']), port=target['port'], service=target['service']).get_target())
