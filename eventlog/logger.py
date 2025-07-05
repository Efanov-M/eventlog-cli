import os
from datetime import datetime


def read_logs():
    if os.path.isfile("eventlog.log"):
        with open("eventlog.log", "r") as file:
            content = file.readlines()  # получаем список строк
            return content
    else:
        return ["Файл логов не найден.\n"]


def log_event(event_type, level, message):
    if os.path.isfile("eventlog.log"):
        with open("eventlog.log", "a") as file:
            log_time = datetime.now()
            log_str = f"{log_time.strftime("%d.%m.%Y %H:%M:%S")} {event_type} {level} {message}"
            file.write(f"{log_str}/n")
    else:
        with open("eventlog.log", "x") as file:
            return
