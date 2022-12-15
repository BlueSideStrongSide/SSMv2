# Windows Service To Monitor and Alert when needed for the home lab
from src.hg_service_monitor import HGServiceMonitor

test = HGServiceMonitor(notify_status=False)

test.enable_service_monitor()
