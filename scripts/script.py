from modules import script_callbacks  # pylint: disable=import-error

from scripts.api import on_app_started

script_callbacks.on_app_started(on_app_started)