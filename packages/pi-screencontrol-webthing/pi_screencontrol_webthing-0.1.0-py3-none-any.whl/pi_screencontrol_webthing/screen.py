import os
from datetime import datetime, timedelta
from threading import Thread
from time import sleep


class Screen:

    XSET_CMD = "XAUTHORITY=~pi/.Xauthority DISPLAY=:0 xset "

    def __init__(self, log_listener, status_listener, command_log_size: int = 40):
        self.log_listener = log_listener
        self.status_listener = status_listener
        self.command_log_size = command_log_size
        self.timeout_sec = 180  # 3 min
        self.date_update_sent = datetime.now()
        self.show_display_until = datetime.now()
        self.command_log = list()
        self.update_timeout(self.timeout_sec)

    def update_timeout(self, timeout_sec: int):
        self.__execute_cmd(self.XSET_CMD + "s " + str(timeout_sec))
        self.__execute_cmd(self.XSET_CMD + "dpms " + str(timeout_sec) + " " + str(timeout_sec) + "  " + str(timeout_sec))
        self.timeout_sec = timeout_sec

    @property
    def is_on(self) -> bool:
        return self.date_update_sent + timedelta(seconds=self.timeout_sec) > datetime.now()

    def __notify_state_later(self):
        sleep(self.timeout_sec + 3)
        self.__notify_status_listener()

    def show_display(self, activate: bool):
        if activate:
            now = datetime.now()
            if now > (self.date_update_sent + timedelta(seconds=1)):
                self.__execute_cmd(self.XSET_CMD + "dpms force on")
                self.date_update_sent = now
                self.__notify_status_listener()
                Thread(target=self.__notify_state_later, daemon=True).start()

    def __execute_cmd(self, cmd: str):
        try:
            os.system(cmd)
            self.__log("[" + datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + "]  " + cmd)
        except Exception as e:
            self.__log("[" + datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + "]  " + str(e))

    def __log(self, log_msg: str):
        self.command_log.append(log_msg)
        while len(self.command_log) > 100:
            self.command_log.pop(0)
        try:
            self.log_listener(self.command_log)
        except Exception as e:
            print(e)

    def __notify_status_listener(self):
        try:
            self.status_listener(self.is_on)
        except Exception as e:
            print(e)