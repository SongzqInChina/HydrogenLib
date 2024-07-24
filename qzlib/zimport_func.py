import importlib
import logging
import os.path

from . import zsystem

# module end

zimport_func_logger = logging.getLogger("SzQlib.zimport_func")


def load_module(name, package=...):
    return importlib.import_module(name, package)


def reload_module(module):
    return importlib.reload(module)


def load_path(__path):
    env_pool = zsystem.get_new_pool()

    directory = os.path.dirname(__path)

    env = zsystem.make_env(zsystem.os_env_dict())
    env.get("PATH").append(directory)
    env_pool.add(env, "LOADTEMP")

    env_pool.activate("LOADTEMP")

    module_name = os.path.basename(__path)
    module = load_module(module_name)

    env_pool.activate("Base")

    return module


zimport_func_logger.debug("Module zimport_func loading ...")
