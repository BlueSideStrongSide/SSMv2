import asyncio
import aiohttp
import configparser
from pathlib import Path, PurePath


class PushOver:

    def __init__(self):
        self.token_api_key = None
        self.user_api_key = None
        self.pushover_token_api_key = None
        self.pushover_user_api_key = None
        self.params = None
        self.pushover_url = "https://api.pushover.net/1/messages.json"
        self.configuration_parser = configparser.ConfigParser(strict=False)
        self._read_config()

    def _read_config(self):

        root = Path(__file__).parents[3]
        child = Path("config/notifications/pushover/config.ini")
        config_path = PurePath(root, child)

        try:
            self.targets_configuration = self.configuration_parser.read(config_path)
            self.pushover_token_api_key = self.configuration_parser["NOTIFY"]["pushover_token_api_key"]
            self.pushover_user_api_key = self.configuration_parser["NOTIFY"]["pushover_user_api_key"]
        except Exception as e:
            print(f"UNABLE TO LOCATE CONFIGURATION FILE {config_path}")
            print(f'{config_path} {e}')
            exit()

    async def send_alert(self, message=None):

        self.params = {'token': self.pushover_token_api_key, 'user': self.pushover_user_api_key, 'message': message}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.pushover_url, params=self.params) as resp:
                return resp.status


if __name__ == '__main__':
    test = PushOver()
    asyncio.get_event_loop().run_until_complete(test.send_alert())
