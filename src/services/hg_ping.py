from icmplib import ping, async_ping
from src.notifications.pushover.notifications import PushOver as push_notify
import asyncio


# move to **kwargs
# Exceptions are not being handled correctly
class HGPingServiceMonitor:
    def __init__(self,
                 target,
                 interval=1,
                 count=1,
                 _ping_count=None,
                 _target_options=None,
                 _results_tracker=None,
                 internal_logger=None):

        self._ping_results = None
        self._target = target
        self._target_options = _target_options
        self._interval = interval
        self._ping_count = _ping_count
        self._ping_results_tracker = []  # List made of dicts with keys to track pass or fail?
        self._results_tracker = _results_tracker  # <-- Class result to implement later
        self._internal_logger = internal_logger
        self._failure_counter = int(self._target_options['failure_count'])

        self._timeout = 2
        self._privileged = False
        self._alert_enabled = self._target_options['alert'] or False
        self._alert_throttle = 1 or None

        self.pushover_notifier = push_notify()

    @property
    def success_char(self):
        return u'\u2705'

    @property
    def fail_char(self):
        return u'\u274C'

    @property
    def dispatch_alert_conditions_met(self):
        if len(self._ping_results_tracker) >= self._failure_counter and self._alert_enabled:
            self._ping_results_tracker = []
            return True
        return False

    async def ping_target(self):
        _internal_count = 0

        while True:
            if _internal_count == self._ping_count:
                break

            self._ping_results = await async_ping(self._target, count=1, timeout=self._timeout,
                                                  privileged=self._privileged)

            status_char = self.success_char if not self._ping_results.packet_loss == 1 else self.fail_char

            message = f'{status_char} Ping Target:{self._target} --> ' \
                      f'Packets Sent:{self._ping_results._packets_sent} --> ' \
                      f'Packets Recieved:{self._ping_results.packets_received} --> ' \
                      f'Packets RTT:{self._ping_results.rtts}  ' \
                      f'--> Packets Loss:{self._ping_results.packet_loss}'

            # Log the result
            self._internal_logger.info(message)

            if status_char == u'\u274C' and self.dispatch_alert_conditions_met:
                await self.pushover_notifier.send_alert(message=message)

            self._ping_results_tracker.append(self._ping_results)

            _internal_count += 1  # <-- decide if we want to keep this currently not used
            _internal_wait = 0

            for i in range(1, int(self._interval)):
                await asyncio.sleep(1)


if __name__ == '__main__':
    target_test = {'target': 'raspberrypi', 'service': 'PING', 'interval': '30', 'alert': 'TRUE'}
    asyncio.run(HGPingServiceMonitor(target=target_test['target'], interval=int(target_test['interval'])).ping_target())
