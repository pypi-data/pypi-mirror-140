try:
    from dbus import SystemBus, PROPERTIES_IFACE
except ModuleNotFoundError:
    pass

from sys import platform
from threading import Timer

class NtpServerHandler():
    def __init__(self, disable_dbus: bool = False):
        self.on_ntp_server_synchronized = None
        self.__disable_dbus = disable_dbus
        self.ntp_server_is_synchronized = self._get_ntp_server_synchronized_state()
        self.__timer_interval = 0
        self._timeout_treshold = 300
        if not self.ntp_server_is_synchronized:
            Timer(self.__timer_interval, self._wait_on_ntp_synchronization).start()

    def _get_ntp_server_synchronized_state(self) -> bool:
        if not platform.startswith('linux') or self.__disable_dbus:
            return True

        bus_name = 'org.freedesktop.timedate1'

        bus = SystemBus()
        timedate_obj = bus.get_object(bus_name, '/org/freedesktop/timedate1')
        return bool(timedate_obj.Get(bus_name, 'NTPSynchronized', dbus_interface=PROPERTIES_IFACE))

    def _wait_on_ntp_synchronization(self):
        self.ntp_server_is_synchronized = self._get_ntp_server_synchronized_state()

        if self.on_ntp_server_synchronized is not None and self.ntp_server_is_synchronized:
            self.on_ntp_server_synchronized()

        if not self.ntp_server_is_synchronized:
            self.__timer_interval = self.__timer_interval + 1
            if self.__timer_interval > self._timeout_treshold:
                raise TimeoutError
            Timer(self.__timer_interval, self._wait_on_ntp_synchronization).start()