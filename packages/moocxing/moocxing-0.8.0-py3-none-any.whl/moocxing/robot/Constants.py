import os

PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

APP_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

PACKAGE_PATH = os.path.join(APP_PATH, "package/")

MUSIC_PATH = os.path.join(APP_PATH, "music/")

PLUGIN_PATH = os.path.join(APP_PATH, "plugins/")
CUSTOM_PLUGIN_PATH = "plugins/"

ROBOT_PATH = os.path.join(APP_PATH, "robot/")
STATIC_PATH = os.path.join(APP_PATH, ROBOT_PATH, "static/")
TEMP_PATH = os.path.join(APP_PATH, ROBOT_PATH, "temp/")

# DEFAULT_CONFIG_PATH = os.path.join(STATIC_PATH, 'default.yaml')
DEFAULT_CONFIG_PATH = "default.yaml"
CUSTOM_CONFIG_PATH = "config.yaml"
