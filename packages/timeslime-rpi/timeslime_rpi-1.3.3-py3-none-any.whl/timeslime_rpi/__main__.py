#!/usr/bin/env python3
from os.path import expanduser, join
from threading import Timer
from signal import pause
from threading import Timer

from gpiozero import Button, LED
from requests import HTTPError
import tm1637

from timeslime.handler import (
    DatabaseHandler,
    SettingsHandler,
    StateHandler,
    TimeslimeHandler,
    NtpServerHandler,
)
from timeslime_rpi.handler import DisplayHandler

CANCEL_SCRIPT = False

def toggle_time(timespan_handler):
    if timespan_handler.is_running() is False:
        timespan_handler.start_time()
    else:
        timespan_handler.stop_time()

def display_timespan(display_handler: DisplayHandler, timeslime_handler: TimeslimeHandler):
    global CANCEL_SCRIPT
    if CANCEL_SCRIPT:
        return
    timespan = timeslime_handler.get_elapsed_time()
    display_handler.timedelta_to_display(timespan)
    Timer(1, display_timespan, [display_handler, timeslime_handler]).start()

def start_timeslime(tm: tm1637.TM1637, database_handler: DatabaseHandler, ntp_server_handler: NtpServerHandler):
    global CANCEL_SCRIPT
    status_led = LED(27)
    try:
        state_handler = StateHandler(database_handler)
        settings_handler = SettingsHandler(database_handler, state_handler)
        timeslime_handler = TimeslimeHandler(
            settings_handler,
            database_handler,
            ntp_server_handler,
            state_handler,
            settings_handler.timeslime_server_handler,
        )
        display_handler = DisplayHandler()
        display_handler.on_property_change = tm.numbers
        if timeslime_handler.is_running():
            status_led.on()
        timeslime_handler.on_start = status_led.on
        timeslime_handler.on_stop = status_led.off
        button = Button(17)
        button.when_pressed = lambda: toggle_time(timeslime_handler)
        display_timespan(display_handler, timeslime_handler)
        pause()
    finally:
        CANCEL_SCRIPT = True
        status_led.off()
        tm.write([0, 0, 0, 0])


def main():
    tm = tm1637.TM1637(clk=3, dio=2)
    tm.show('INIT')
    database = join(expanduser('~'), '.timeslime', 'data.db')
    try:
        database_handler = DatabaseHandler(database)
        ntp_server_handler = NtpServerHandler()
        ntp_server_handler.on_ntp_server_synchronized = lambda: start_timeslime(tm, database_handler, ntp_server_handler)
        if ntp_server_handler.ntp_server_is_synchronized:
            start_timeslime(tm, database_handler, ntp_server_handler)
    except HTTPError:
        tm.show('ERR')
        raise
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
