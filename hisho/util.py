import types
import click
import logging
from functools import wraps
from cm_api.api_client import ApiException, ApiResource
from hisho.config import Config

LOG = logging.getLogger(__name__)

def api_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ApiException, e:
            LOG.exception('got API exception')
            raise click.UsageError('API command failed (%s). \n\nUse --debug to '
              'print more information.' % e.args[0])
        return result
    return wrapper

class APIWrapper(object):
    def __init__(self, api_resource):
        self.api_resource = api_resource

    def __getattr__(self, name):
        obj = getattr(self.api_resource, name)

        if isinstance(obj, (types.MethodType, types.FunctionType)):
            result = api_wrapper(obj)
        else:
            result = obj
        return result

class Context(object):
    def __init__(self):
        self.config = Config()
        self.api = APIWrapper(ApiResource(
          self.config.get('host'),
          self.config.get('port'),
          self.config.get('username'),
          self.config.get('password'),
          use_tls = self.config.get('use_tls'),
        ))
        self.cluster = None
        self.service = None

    def setup_service(self, name):
        self.service = APIWrapper(self.cluster.get_service(name))

    def setup_cluster(self, name):
        self.cluster = APIWrapper(self.api.get_cluster(name))
