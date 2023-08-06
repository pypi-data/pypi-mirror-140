#!/usr/bin/env python3
import sys
from datetime import timedelta
from os.path import expanduser, join

import click
from peewee import OperationalError

from timeslime.handler import (
    DatabaseHandler,
    NtpServerHandler,
    SettingsHandler,
    StateHandler,
    TimeslimeHandler,
)
from timeslime.models import Setting

DATABASE_PATH = join(expanduser('~'), '.timeslime', 'data.db')

def boot(config = {'database': DATABASE_PATH}) -> TimeslimeHandler:
    if not 'debug' in config:
        debug = False
    else:
        debug = config['debug']
    database_path = config['database']
    database_handler = DatabaseHandler(database_path)
    state_handler = StateHandler(database_handler)
    settings_handler = SettingsHandler(database_handler, state_handler)
    ntp_server_handler = NtpServerHandler(debug)

    return TimeslimeHandler(
        settings_handler,
        database_handler,
        ntp_server_handler,
        state_handler,
        settings_handler.timeslime_server_handler,
    )


@click.group()
@click.option('--database', default=DATABASE_PATH, help='Defines path to the database. [ default: ~/.timeslime/data.db ]')
@click.pass_context
def main(ctx, database):
    """It's a tool to track your time."""
    ctx.ensure_object(dict)
    ctx.obj['database'] = database

@main.command('start', short_help='Start your time')
@click.pass_context
def start(ctx):
    timeslime_handler = boot(ctx.obj)
    timeslime_handler.start_time()

@main.command('stop', short_help='Stop your time')
@click.pass_context
def stop(ctx):
    timeslime_handler = boot(ctx.obj)
    timeslime_handler.stop_time()

@main.command('display', short_help='Display your time')
@click.pass_context
def display(ctx):
    timeslime_handler = boot(ctx.obj)
    elapsed_time = str(abs(timeslime_handler.get_elapsed_time()))
    print(elapsed_time)

@main.command('settings', short_help='Get or set a setting')
@click.pass_context
@click.option('--key', required=True, help='defines setting key')
@click.option('--value', help='defines setting value')
@click.option('--delete', is_flag=True, help='delete a setting')
def settings(ctx, key, value, delete):
    """Get or set a setting. If value is set it will create or overwrite the setting."""
    database_handler = DatabaseHandler(ctx.obj['database'])
    settings_handler = SettingsHandler(database_handler)

    if delete:
        if settings_handler.contains(key):
            setting = settings_handler.get(key)
            print('Old setting was: "%s" with value: "%s"' % (key, setting.value))
            settings_handler.delete(key)
            print('Deleted setting: "%s"' % (key))
        else:
            print('There is no setting for: "%s"' % key)
        return

    if not value:
        if settings_handler.contains(key):
            setting = settings_handler.get(key)
            print('Setting: "%s" is "%s"' % (key, setting.value))
        else:
            print('There is no setting for: "%s"' % key)
    else:
        if settings_handler.contains(key):
            setting = settings_handler.get(key)
            print('Old setting was: "%s" with value: "%s"' % (key, setting.value))
            setting.value = value
        else:
            setting = Setting()
            setting.key = key
            setting.value = value
        settings_handler.set(setting)
        print('Set setting: "%s" to "%s"' % (key, value))

@main.command('init', short_help='Initialize timeslime')
@click.pass_context
@click.option(
    "--weekly_hours",
    type=click.INT,
    prompt="How many hours do you have to work a week?",
)
@click.option(
    "--timeslime_server",
    type=click.STRING,
    default="",
    prompt="Do you want to connect to a timeslime-server (e.g. http://localhost:8000/)?",
)
@click.option(
    "--timeslime_username",
    type=click.STRING,
    default="",
    prompt="What is your timeslime-server username?",
)
@click.option(
    "--timeslime_password",
    type=click.STRING,
    hide_input=True,
    default="",
    prompt="What is your timeslime-server password?",
)
def init(ctx, weekly_hours, timeslime_server, timeslime_username, timeslime_password):
    """initialize timeslime"""
    week = timedelta(hours=weekly_hours)
    daily_hours = week / 5
    weekly_hours_array = [
        str(daily_hours),
        str(daily_hours),
        str(daily_hours),
        str(daily_hours),
        str(daily_hours),
        str(timedelta()),
        str(timedelta()),
    ]

    database_handler = DatabaseHandler(ctx.obj["database"])
    settings_handler = SettingsHandler(database_handler)

    if not (
        timeslime_server is None or not timeslime_server or timeslime_server.isspace()
    ):
        if (
            timeslime_username is None
            or not timeslime_username
            or timeslime_username.isspace()
        ):
            print("Username could not be empty.")
            sys.exit(1)

        if (
            timeslime_password is None
            or not timeslime_password
            or timeslime_password.isspace()
        ):
            print("Password could not be empty.")
            sys.exit(1)

        timeslime_server_setting = Setting()
        timeslime_server_setting.key = "timeslime_server"
        timeslime_server_setting.value = timeslime_server
        settings_handler.set(timeslime_server_setting)
        timeslime_username_setting = Setting()
        timeslime_username_setting.key = "username"
        timeslime_username_setting.value = timeslime_username
        settings_handler.set(timeslime_username_setting)
        timeslime_password_setting = Setting()
        timeslime_password_setting.key = "password"
        timeslime_password_setting.value = timeslime_password
        settings_handler.set(timeslime_password_setting)
    else:
        if settings_handler.contains("timeslime_server"):
            settings_handler.delete("timeslime_server")
        if settings_handler.contains("username"):
            settings_handler.delete("username")
        if settings_handler.contains("password"):
            settings_handler.delete("password")

    weekly_hours_setting = Setting()
    weekly_hours_setting.key = "weekly_hours"
    weekly_hours_setting.value = weekly_hours_array
    settings_handler.set(weekly_hours_setting)


@main.command("update", short_help="Update database")
@click.pass_context
def update(ctx):
    """update database"""
    database_handler = DatabaseHandler(ctx.obj["database"])
    try:
        database_handler.update()
        print("Updated database")
    except OperationalError:
        print("Database is already updated")


@main.command("sync", short_help="Sync timeslime with server")
@click.pass_context
def sync(ctx):
    """manually sync"""
    timeslime_handler = boot(ctx.obj)
    timeslime_handler.settings_handler.sync(True)
    timeslime_handler.sync(True)


if __name__ == "__main__":
    main(obj={})
