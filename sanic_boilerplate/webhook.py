import re

from sanic_boilerplate.exceptions import FdkInvalidWebhookConfig


class WebhookRegistry:
    def __init__(self):
        self._handler_map = None
        self._config = None
        self._fdk_config = None

    def initialize(self, config, fdk_config):
        email_regex_match = "^\S+@\S+\.\S+$"
        if not config.get("notification_email") or not re.findall(email_regex_match, config["notification_email"]):
            raise FdkInvalidWebhookConfig("Invalid or missing notification_email")

        if not config.get("api_path") or config["api_path"][0] != "/":
            raise FdkInvalidWebhookConfig("Invalid or missing api_path")

        if not config.get("event_map"):
            raise FdkInvalidWebhookConfig("Invalid or missing event_map")

        config["subscribe_on_install"] = True if not config.get("subscribe_on_install") else config[
            "subscribe_on_install"]
        self._handler_map = {}
        self._config = config
        self._fdk_config = fdk_config

        for event_name, handler_data in self._config["event_map"].items():
            self._handler_map[event_name] = handler_data

    def is_initialized(self):
        return not self._handler_map and self._config["subscribe_on_install"]
