"""handler for states"""
from datetime import datetime

from timeslime.handler.database_handler import DatabaseHandler
from timeslime.models import State


class StateHandler:
    """class for state handler"""

    def __init__(self, database_handler: DatabaseHandler):
        self.database_handler = database_handler
        self._state: State = State.get_or_create()[0]

    def set_last_setting_sync(self, date: datetime):
        """set last_setting_sync property
        :param data: defines date to be set"""
        if not isinstance(date, datetime):
            raise ValueError

        self._state.last_setting_sync = date
        self.database_handler.save_state(self._state)

    def set_last_timespan_sync(self, date: datetime):
        """set last_timespan_sync property
        :param data: defines date to be set"""
        if not isinstance(date, datetime):
            raise ValueError

        self._state.last_timespan_sync = date
        self.database_handler.save_state(self._state)

    def get_state(self) -> State:
        """get state"""
        return self._state
