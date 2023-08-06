import pkgutil
from moocxing.robot import Constants

import logging

log = logging.getLogger(__name__)


def loadPlugin(MODULE):
    plugins = []
    chat = None
    locations = [
        Constants.CUSTOM_PLUGIN_PATH,
        Constants.PLUGIN_PATH
    ]

    for finder, name, ispkg in pkgutil.walk_packages(locations):
        loader = finder.find_module(name)

        mod = loader.load_module(name)

        if not hasattr(mod, 'Plugin'):
            continue

        plugin = mod.Plugin(MODULE)

        if plugin in plugins:
            continue

        if plugin.SLUG == "chat":
            chat = plugin
        else:
            plugins.append(plugin)

        log.info("-" * 35)
        log.info(f">>> 插件加载成功 {plugin.SLUG}")

    log.info("-" * 35)
    log.info(">>> 插件加载完成\n\n")

    return plugins, chat
