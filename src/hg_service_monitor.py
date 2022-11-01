import logging
import configparser
import asyncio
from pathlib import Path
from src.services.hg_ping import HGPingServiceMonitor
from src.services.hg_http import HGHttpServiceMonitor
from src.util.result_handler import HGResultHandler
from src.notifications.pushover.notifications import PUSHOVER as pushover_notifications

class HGServiceMonitor:

    def __init__(self, targets_config=None, output_log=None):
        self.logger = None
        self.targets = None
        self.enabled_targets = []
        self.disabled_targets = None
        self.pushover_notifier = pushover_notifications()
        self._ssm_result = HGResultHandler()

        self.targets_config_file = targets_config or "config/targets/targets.ini"  # <-- make cross platform ready
        self.output_log = output_log or "src/logs/hg_logmonitor.log"
        self.configuration_parser = configparser.ConfigParser(strict=False)

    def enable_service_monitor(self):
        # start async main loop
        asyncio.run(self.async_monitor_startup())

    async def async_monitor_startup(self):
        await self.logging_startup()
        launch_routines = [self.read_config()]

        res = await asyncio.gather(*launch_routines, return_exceptions=True)

        if not res == [None]: # <-- script failed to startup
            await self.failed_startup(fail_reason=res)

        await self.add_monitor_targets()
        await self._monitor_target()

    async def failed_startup(self, fail_reason=None):
        self.logger.debug("An error occured during startup the program will now exit")
        print(fail_reason)
        exit()

    async def logging_startup(self):
        self.logger = logging.getLogger('HGServiceMonitor')
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        console_h = logging.StreamHandler()
        
        requested_log_file = Path(self.output_log)
        if not requested_log_file.is_file():
            Path(self.output_log).mkdir(parents=True, exist_ok=True)
        file_h = logging.FileHandler(filename=self.output_log, mode="a+", encoding="utf8")


        # provide option to set console loggin from configuration file
        console_h.setLevel(logging.DEBUG)
        file_h.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s  ')

        # add formatter to ch
        console_h.setFormatter(formatter)
        file_h.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(console_h)
        self.logger.addHandler(file_h)

        #log message
        self.logger.info("HGServiceMonitor is online and looking for targets.")

    async def read_config(self, configuration="config/targets/targets.ini"):

        self.logger.info("HGServiceMonitor configuration file import started")

        try:
            self.targets_configuration = self.configuration_parser.read(self.targets_config_file)
        except Exception as e:
            self.logger.info(e)

        self.logger.info("HGServiceMonitor configuration file import finished")

    async def add_monitor_targets(self, targets_config=None):

        for host in self.configuration_parser.sections():
            building_targets = {}
            building_targets["target"] = host
            for key, value in self.configuration_parser[host].items():
                building_targets[key] = value
            self.enabled_targets.append(building_targets)

        self.logger.info(f"Enabled Targets: {self.enabled_targets}")

        # Alert on startup
        await self.pushover_notifier._send_alert(f"Enabled Targets: {self.enabled_targets}")

        return self.enabled_targets

    async def _monitor_target(self):
        self.logger.info(f"HGServiceMonitor is starting attemtping to monitor {len(self.enabled_targets)} target(s).")
        await self.pushover_notifier._send_alert(message=f"HGServiceMonitor is starting attemtping to monitor {len(self.enabled_targets)} target(s).")
        service_dispatcher = []
        for target in self.enabled_targets:
            if target['service'] == "ICMP":

                # only pass _target_options and parse the values within the service monitor
                service_dispatcher.append(HGPingServiceMonitor(target=target['target'],
                                                               interval=float(target['interval']),
                                                               _target_options = target,
                                                               _results_tracker=self._ssm_result,
                                                               internal_logger=self.logger).ping_target())

            elif target['service'] == "HTTP" or "HTTPS":

                service_dispatcher.append(HGHttpServiceMonitor(target=target['target'],
                                                               interval=float(target['interval']),
                                                               port=target.get('port'),
                                                               service=target['service'],
                                                               _target_options=target,
                                                               _results_tracker=self._ssm_result,
                                                               internal_logger=self.logger).get_target())


        while self.enabled_targets:
            res = await asyncio.gather(*service_dispatcher, return_exceptions=True)
            # add a check to remove monitor items... hardlinks on async task may help remove them
            # excpetions should be returned and remove the target from the list
            if res:
                # need to sort through errors
                print(res)

        # while self.enabled_targets:
        #     for coro in asyncio.as_completed(service_dispatcher):
        #         earliest_result= await coro
        #         print(earliest_result)

    async def remove_monitor_target(self):
        loop_count = 1
        while self.enabled_targets:
            random_sleep = random.randint(1, 5)
            self.logger.info(f"HGServiceMonitor is online and removing {loop_count} target(s).")
            await asyncio.sleep(random_sleep)
            loop_count += random.randint(1, 5)

    async def close_monitor_target(self):
        pass

if __name__ == 'main':
    test = HGServiceMonitor()
