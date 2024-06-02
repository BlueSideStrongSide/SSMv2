import logging
import configparser
import asyncio
from pathlib import Path
from src.services.hg_ping import HGPingServiceMonitor
from src.services.hg_http import HGHttpServiceMonitor
from src.util.result_handler import HGResultHandler
from src.notifications.pushover.notifications import PushOver as push_notify


class HGServiceMonitor:
    
    def __init__(self,
                 targets_config: str = "config/targets/targets.ini",
                 output_log: str = "/logs/hg_logmonitor.log",
                 web_tail_logs=True,
                 notify_status: bool = True):
        """

        :param targets_config Specify the full path to the configuration file
        :param output_log Specify the full path to the output log file
        :param notify_status:bool  Should the service monitor send notifications during startup
        """
        self.pushover_notifier = push_notify()
        self._ssm_result = HGResultHandler()
        
        self.notify_status = notify_status
        self.targets_configuration = None
        
        self.enabled_targets = []
        self.targets = None
        self.disabled_targets = None
        self.targets_config_file = targets_config  # <-- make cross platform ready
        self.configuration_parser = configparser.ConfigParser(strict=False)
        self.logger = None
        self.output_log = output_log
    
    def enable_service_monitor(self):
        # start async main loop
        asyncio.run(self.async_monitor_startup())
    
    async def logging_startup(self):
        self.logger = logging.getLogger('HGServiceMonitor')
        self.logger.setLevel(logging.DEBUG)
        
        # create console handler and set level to debug
        console_h = logging.StreamHandler()
        
        requested_log_file = Path(self.output_log)
        
        if not requested_log_file.is_file():
            Path(requested_log_file.parent).mkdir(parents=True, exist_ok=True)
        
        file_h = logging.FileHandler(filename=self.output_log, mode="a+", encoding="utf8")
        
        console_h.setLevel(logging.INFO)
        file_h.setLevel(logging.DEBUG)
        
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s  ')
        
        # add formatter to ch
        console_h.setFormatter(formatter)
        file_h.setFormatter(formatter)
        
        # add ch to logger
        self.logger.addHandler(console_h)
        self.logger.addHandler(file_h)
        
        # log message
        self.logger.info("HGServiceMonitor is online and looking for targets.")
    
    async def async_monitor_startup(self):
        #start logging
        await self.logging_startup()
        
        #read provided configuration
        launch_routines = [self.read_config()]
        
        #there may not be a need for gather here?
        res = await asyncio.gather(*launch_routines, return_exceptions=True)
        
        if not res == [None]:  # <-- script failed to startup
            await self.failed_startup(fail_reason=res)
        
        await self.add_monitor_targets()
        await self._monitor_target()
    
    async def failed_startup(self, fail_reason=None):
        self.logger.debug("An error occurred during startup the program will now exit")
        print(fail_reason)
        exit()
    
    async def read_config(self, configuration="config/targets/targets.ini"):
        
        self.logger.info("HGServiceMonitor configuration file import started")
        
        try:
            self.targets_configuration = self.configuration_parser.read(self.targets_config_file)
        except Exception as e:
            self.logger.info(e)
        
        self.logger.info("HGServiceMonitor configuration file import finished")
    
    async def add_monitor_targets(self, targets_config=None):
        
        self.logger.debug([item for item in self.configuration_parser.items()])
        
        for host in self.configuration_parser.sections():
            
            building_targets = {"target": host}
            for key, value in self.configuration_parser[host].items():
                if key in ["alert", "ms_check"]:
                    
                    if value.lower() == "true":
                        value = True
                    else:
                        value = False
                
                building_targets[key] = value
            
            self.enabled_targets.append(building_targets)
        
        self.logger.info(f"Enabled Targets: {self.enabled_targets}")
        
        # Alert on startup
        if self.notify_status:
            await self.pushover_notifier.send_alert(f"Enabled Targets: {self.enabled_targets}")
        
        return self.enabled_targets
    
    async def _monitor_target(self):
        self.logger.info(f"HGServiceMonitor is starting attempting to monitor {len(self.enabled_targets)} target(s).")
        
        if self.notify_status:
            await self.pushover_notifier.send_alert(
                message=f"HGServiceMonitor is starting attempting to monitor {len(self.enabled_targets)} target(s).")
        
        service_dispatcher = []
        for target in self.enabled_targets:
            
            if target['service'] == "ICMP":
                
                # only pass _target_options and parse the values within the service monitor
                service_dispatcher.append(HGPingServiceMonitor(target=target['target'],
                                                               interval=float(target['interval']),
                                                               _target_options=target,
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
        
        # task added to list above, this list will not be sent to gather to perform monitoring asynchronously
        while self.enabled_targets:
            res = await asyncio.gather(*service_dispatcher, return_exceptions=True)
            # add a check to remove monitor items... hardlinks on async task may help remove them
            # exceptions should be returned and remove the target from the list
            if res:
                # need to sort through errors
                print(res)
                break
    
    async def close_monitor_target(self):
        pass


if __name__ == 'main':
    test = HGServiceMonitor()
