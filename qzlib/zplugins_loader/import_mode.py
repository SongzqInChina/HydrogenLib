import queue
from queue import Queue
from types import *

from .. import zimport_func
from ..zother import cglobalc as Namespace

namespace = Namespace()
buffer_queue = Queue()


class PluginError(BaseException):
    def __init__(self, errortype, plugin_name, message):
        self.error_type = errortype
        self.plugin_name = plugin_name
        self.message = message

    def __str__(self):
        return f'Plugin{self.error_type}Error: {self.plugin_name} - {self.message}'


class PluginClient:
    def __init__(self, name, module: ModuleType):
        module.register_plugin(name, self)


class PluginOptions:
    def __init__(
            self,
            name: str,
            version: str,
            client: PluginClient
    ):
        self.name = name
        self.version = version
        self.client = client


class PluginServer:
    def __init__(self, globals_dict=globals()):
        self.plugins = {}
        self.globals = globals_dict

    def _load_plugin(self, path):
        moudule = zimport_func.load_path(path)
        try:
            options = buffer_queue.get(timeout=5)
        except queue.Empty:
            raise PluginError('Load', None, "Plugin load timeout.")
        self.plugins[options.name] = options


def register_options(options):
    buffer_queue.put(options)


