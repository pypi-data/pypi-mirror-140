"""collection of data models"""
from datetime import datetime, timezone
from uuid import uuid4

from peewee import DateTimeField, Model, TextField, UUIDField

DateTimeField.formats = [
    "%Y-%m-%d %H:%M:%S.%f%z",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
]

class Setting(Model):
    """setting model"""

    id = UUIDField(primary_key=True, default=uuid4)
    key = TextField(index=True, null=True)
    value = TextField(null=True)
    created_at = DateTimeField(
        default=lambda: datetime.now(tz=timezone.utc), null=False
    )
    updated_at = DateTimeField(
        default=lambda: datetime.now(tz=timezone.utc), null=False
    )

    class Meta:
        """defines meta information"""

        table_name = "settings"


class SettingResponse:
    """setting response model"""

    settings: list
    request_time: datetime


class Timespan(Model):
    """timespan model"""

    id = UUIDField(primary_key=True, default=uuid4)
    start_time = DateTimeField(null=True)
    stop_time = DateTimeField(null=True)
    created_at = DateTimeField(
        default=lambda: datetime.now(tz=timezone.utc), null=False
    )
    updated_at = DateTimeField(
        default=lambda: datetime.now(tz=timezone.utc), null=False
    )

    class Meta:
        """defines meta information"""

        table_name = "timespans"


class TimespanResponse:
    """timespan response model"""

    timespans: list
    request_time: datetime


class State(Model):
    """state model"""

    id = UUIDField(primary_key=True, default=uuid4)
    last_setting_sync = DateTimeField(null=True)
    last_timespan_sync = DateTimeField(null=True)
    created_at = DateTimeField(
        default=lambda: datetime.now(tz=timezone.utc), null=False
    )
    updated_at = DateTimeField(
        default=lambda: datetime.now(tz=timezone.utc), null=False
    )

    class Meta:
        """defines meta information"""

        table_name = "states"
