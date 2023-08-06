"""collection of serializer classes"""
from datetime import datetime
from json import loads
from uuid import UUID

from timeslime.models import Setting, Timespan


class TimespanSerializer:
    """serializer for a timespan object"""

    @classmethod
    def deserialize(cls, json_string: str) -> Timespan:
        """deserialize a json string into a Timespan object
        :param json_string: defines json string"""
        if isinstance(json_string, str):
            timespan_object = loads(json_string)
        else:
            timespan_object = json_string

        timespan = Timespan()

        if 'id' in timespan_object:
            timespan.id = UUID(timespan_object['id'])

        if (
            timespan_object["start_time"] == "None"
            or timespan_object["start_time"] is None
        ):
            raise KeyError

        timespan.start_time = datetime.fromisoformat(timespan_object["start_time"])

        if "stop_time" in timespan_object and not (
            timespan_object["stop_time"] == "None"
            or timespan_object["stop_time"] is None
        ):
            timespan.stop_time = datetime.fromisoformat(timespan_object["stop_time"])

        if "created_at" in timespan_object and timespan_object["created_at"] != "None":
            timespan.created_at = datetime.fromisoformat(timespan_object["created_at"])
        if "updated_at" in timespan_object and timespan_object["updated_at"] != "None":
            timespan.updated_at = datetime.fromisoformat(timespan_object["updated_at"])

        return timespan

    @classmethod
    def serialize(cls, timespan: Timespan):
        """serialize a Timespan object into a string
        :param timespan: defines Timespan object"""

        start_time_str = None
        if timespan.start_time:
            start_time_str = str(timespan.start_time)

        stop_time_str = None
        if timespan.stop_time:
            stop_time_str = str(timespan.stop_time)

        return {
            "id": str(timespan.id),
            "start_time": start_time_str,
            "stop_time": stop_time_str,
            "created_at": str(timespan.created_at),
            "updated_at": str(timespan.updated_at),
        }

    def serialize_list(self, timespans: list):
        """serialize a Timespan object into a string
        :param timespans: defines a list of Timespan object"""
        timespans_json = []
        for timespan in timespans:
            timespans_json.append(self.serialize(timespan))

        return timespans_json


class SettingSerializer:
    """serializer for a setting object"""

    @classmethod
    def deserialize(cls, json_string: str) -> Setting:
        """deserialize a json string into a Setting object
        :param json_string: defines json string"""
        if isinstance(json_string, str):
            setting_object = loads(json_string)
        else:
            setting_object = json_string

        setting = Setting()

        if "id" in setting_object:
            setting.id = UUID(setting_object["id"])

        if setting_object["key"] == "None" or setting_object["key"] is None:
            raise KeyError

        setting.key = setting_object["key"]

        if "value" in setting_object:
            if setting_object["value"] == "None":
                return setting
            setting.value = setting_object["value"]

        if "created_at" in setting_object and setting_object["created_at"] != "None":
            setting.created_at = datetime.fromisoformat(setting_object["created_at"])
        if "updated_at" in setting_object and setting_object["updated_at"] != "None":
            setting.updated_at = datetime.fromisoformat(setting_object["updated_at"])
        return setting

    @classmethod
    def serialize(cls, setting: Setting):
        """serialize a Setting object into a string
        :param setting: defines Setting object"""
        return {
            "id": str(setting.id),
            "key": setting.key,
            "value": setting.value,
            "created_at": str(setting.created_at),
            "updated_at": str(setting.updated_at),
        }

    def serialize_list(self, settings: list):
        """serialize a Setting object into a string
        :param settings: defines a list of Setting object"""
        settings_json = []
        for setting in settings:
            settings_json.append(self.serialize(setting))

        return settings_json
