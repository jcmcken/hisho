from cm_api.api_client import ApiResource
from hisho.config import Config

class API(object):
    def __init__(self, config=None):
        self.config = config or Config()

        self._api = ApiResource(
          self.config.get('host'),
          self.config.get('port'),
          self.config.get('username'),
          self.config.get('password'),
          use_tls = self.config.get('use_tls'),
        )
