"""database handler class"""
from datetime import datetime, timedelta
from os import mkdir
from os.path import dirname, exists, join, realpath
from typing import Union

from peewee import SqliteDatabase

from timeslime.models import Setting, State, Timespan


class DatabaseHandler():
    """database handler class"""
    def __init__(self, database_connection):
        self.is_testing = False
        if isinstance(database_connection, SqliteDatabase):
            self.connection = database_connection
            self.is_testing = True
        else:
            if not exists(database_connection):
                directory = dirname(database_connection)
                if directory != '' and not exists(directory):
                    mkdir(directory)
            self.connection = SqliteDatabase(database_connection)

        models = [Setting, State, Timespan]
        self.connection.bind(models)
        self.connection.create_tables(models)

    def __del__(self):
        if not self.is_testing:
            self.connection.close()

    def update(self):
        """run update on database schema"""
        with open(
            join(dirname(realpath(__file__)), "..", "update", "1.2_to_1.3.sql"),
            "r",
            encoding="utf-8",
        ) as update:
            for line in update.readlines():
                self.connection.execute_sql(line)

    def get_tracked_time_in_seconds(self, today: datetime) -> timedelta:
        """get tracked time in seconds"""
        daily_sum_in_seconds = timedelta(seconds=0)
        utc_offset = timedelta()
        try:
            setting = self.read_setting("utc_offset")
            if setting is not None:
                utc_offset = timedelta(seconds=int(setting.value))
        except Setting.DoesNotExist:  # pylint: disable=no-member
            offset = today.utcoffset()
            if offset is not None:
                utc_offset = offset
        today_utc = (
            datetime(year=today.year, month=today.month, day=today.day) + utc_offset
        )
        cursor = self.connection.execute_sql(
            "SELECT round(sum((julianday(stop_time) - julianday(start_time)) * 24 * 60 * 60))"
            f' as timespan FROM timespans WHERE strftime("{today_utc}") < datetime(start_time);'
        )
        response = cursor.fetchone()[0]
        if response != None:
            daily_sum_in_seconds = timedelta(seconds=response)
        self.connection.commit()
        return daily_sum_in_seconds

    def save_timespan(self, timespan: Timespan) -> Timespan:
        """save timespan
        :param timespan: defines timespan"""
        if not isinstance(timespan, Timespan):
            raise ValueError

        if timespan.start_time is None:
            raise ValueError

        old_timespan = Timespan.get_or_none(Timespan.id == timespan.id)
        if old_timespan is not None:
            if (
                old_timespan.start_time == timespan.start_time
                and old_timespan.stop_time == timespan.stop_time
            ):
                return old_timespan
            old_timespan.start_time = timespan.start_time
            old_timespan.stop_time = timespan.stop_time
            old_timespan.updated_at = datetime.utcnow()
            old_timespan.save()
            return old_timespan
        else:
            timespan.save(force_insert=True)
            return timespan

    def get_recent_timespan(self) -> Timespan:
        """get recent timespan"""
        # pylint: disable=singleton-comparison
        return Timespan.get_or_none(Timespan.stop_time == None)

    def read_timespan(self, guid: str) -> Timespan:
        """read timespan from database
        :param guid: defines id"""
        if not id:
            return None

        return Timespan.get_by_id(guid)

    def read_timespans(self, date: datetime = None) -> list:
        """read all timespans from database"""
        if date:
            return Timespan.select().where(Timespan.updated_at > date)

        return Timespan.select()

    def save_setting(self, setting: Setting) -> Setting:
        """save setting to database
        :param setting: define setting"""
        if not isinstance(setting, Setting):
            raise ValueError

        if setting.key is None:
            raise ValueError

        old_setting = Setting.get_or_none(Setting.key == setting.key)
        if old_setting is not None:
            if setting.value == old_setting.value:
                return old_setting
            old_setting.value = setting.value
            old_setting.updated_at = datetime.utcnow()
            old_setting.save()
            return old_setting
        else:
            setting.save(force_insert=True)
            return setting

    def read_setting(self, key: str) -> Union[Setting, None]:
        """read setting from database
        :param key: defines key"""
        if not key:
            return None

        return Setting.get(Setting.key == key)

    def read_settings(self, date: datetime = None) -> list:
        """read all settings from database"""
        # pylint: disable=singleton-comparison
        if date:
            return Setting.select().where(
                Setting.key != None, Setting.updated_at > date
            )

        return Setting.select().where(Setting.key != None)

    def delete_setting(self, key: str):
        """delete setting from database"""
        if not key:
            return

        query = Setting.delete().where(Setting.key == key)
        query.execute()

    def save_state(self, state: State):
        """save state to database
        :param state: defines state"""
        if not isinstance(state, State):
            raise ValueError

        state.updated_at = datetime.utcnow()
        query = state.delete()
        query.execute()
        state.save(force_insert=True)

    def read_state(self) -> State:
        """rest state from database"""
        return State.get_or_create()
