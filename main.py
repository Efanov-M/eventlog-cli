import argparse
import sys

import eventlog.logger

parser = argparse.ArgumentParser(description="Утилита для ведения журнала событий ")

# создаем ключи


parser.add_argument("--type", type=str, help="тип события ( SYSTEM, USER, NETWORK)")
parser.add_argument("--level", type=str, help="Уровень важности: INFO, WARNING, ERROR")
parser.add_argument("--message", type=str, help="Основной текст события")

# создаем группу
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--add", action="store_true", help="говорит, что нужно добавить запись"
)
group.add_argument("--show", action="store_true", help="")


args = parser.parse_args()

# основная логика

if args.show:
    logs = eventlog.logger.read_logs()
    for line in logs:
        print(line.strip())


if args.add:
    if args.type and args.level and args.message:
        eventlog.logger.log_event(args.type, args.level, args.message)
    else:
        print("❗️Убедитесь, что вы указали --type, --level и --message")
        sys.exit(1)
