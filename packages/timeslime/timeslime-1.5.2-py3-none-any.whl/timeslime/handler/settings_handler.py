"""handler for settings"""
from datetime import datetime, timezone

from peewee import DoesNotExist
from requests.exceptions import ConnectionError as RequestConnectionError

from timeslime.handler import DatabaseHandler, TimeslimeServerHandler
from timeslime.handler.state_handler import StateHandler
from timeslime.models import Setting


class SettingsHandler:
    """ "class for setting handler"""

    def __init__(
        self,
        database_handler: DatabaseHandler,
        state_handler: StateHandler = None,
        timeslime_server_handler: TimeslimeServerHandler = None,
    ):
        self.database_handler = database_handler
        self.state_handler = state_handler
        self.timeslime_server_handler = timeslime_server_handler
        self._set_timeslime_server_handler()
        self.__exclude_settings = ["timeslime_server", "username", "password"]

    def _set_timeslime_server_handler(self):
        if self.timeslime_server_handler is not None:
            return

        if (
            self.contains("timeslime_server")
            and self.contains("username")
            and self.contains("password")
        ):
            timeslime_server = self.get("timeslime_server")
            username = self.get("username")
            password = self.get("password")
            self.timeslime_server_handler = TimeslimeServerHandler(
                timeslime_server.value, username.value, password.value
            )
        else:
            self.timeslime_server_handler = None

    def set(self, setting: Setting) -> None:
        """set a setting
        :param setting: defines a setting"""
        setting = self.database_handler.save_setting(setting)
        if self.timeslime_server_handler is not None:
            try:
                self.timeslime_server_handler.send_setting(setting)
            except RequestConnectionError:
                pass

    def get(self, key: str) -> Setting:
        return self.database_handler.read_setting(key)

    def get_all(self, date: datetime = None) -> list:
        """get all settings"""
        return self.database_handler.read_settings(date)

    def delete(self, key: str):
        return self.database_handler.delete_setting(key)

    def contains(self, key: str) -> bool:
        try:
            self.database_handler.read_setting(key)
            return True
        except DoesNotExist:
            return False

    def sync(self, ignore_state: bool = False) -> None:
        """sync settings with a timeslime server
        :param ignore_state: define to ignore the state (everything will be synchronized)"""
        if self.timeslime_server_handler is not None:
            last_setting_sync = None
            if not ignore_state and self.state_handler:
                last_setting_sync = self.state_handler.get_state().last_setting_sync
            settings_response = self.timeslime_server_handler.get_settings(
                last_setting_sync
            )

            for setting in settings_response.settings:
                if setting.key in self.__exclude_settings:
                    continue
                if not self.contains(setting.key):
                    self.set(setting)
                else:
                    local_setting = self.get(setting.key)
                    if local_setting.updated_at.tzinfo is None:
                        local_setting.updated_at = local_setting.updated_at.replace(
                            tzinfo=timezone.utc
                        )
                    if setting.updated_at.tzinfo is None:
                        setting.updated_at = setting.updated_at.replace(
                            tzinfo=timezone.utc
                        )
                    if local_setting.updated_at < setting.updated_at:
                        self.set(setting)

            sync_settings = list()
            for setting in self.get_all(last_setting_sync):
                if setting.key in self.__exclude_settings:
                    continue
                sync_settings.append(setting)

            if any(sync_settings):
                self.timeslime_server_handler.send_setting_list(sync_settings)

            if self.state_handler:
                self.state_handler.set_last_setting_sync(settings_response.request_time)
