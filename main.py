import argparse
import os
import sys
from datetime import datetime

import eventlog.logger

parser = argparse.ArgumentParser(description="Утилита для ведения журнала событий ")

# создаем ключи


parser.add_argument(
    "--type",
    choices=["SYSTEM", "USER", "APP"],
    metavar="TYPE",
    help="Тип события: SYSTEM | USER | APP",
)

parser.add_argument(
    "--level",
    choices=["INFO", "WARNING", "ERROR"],
    metavar="LEVEL",
    help="Уровень важности: INFO | WARNING | ERROR",
)
parser.add_argument("--message", type=str, help="Основной текст события")
parser.add_argument("--date", type=str, help="дата  события")
parser.add_argument(
    "----keyword",
    type=str,
    help="позволяет фильтровать события по вхождению слова или части текста в поле сообщения ",
)

# создаем группу
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--add", action="store_true", help="говорит, что нужно добавить запись"
)
group.add_argument("--show", action="store_true", help="показ журнала логов")
group.add_argument("--clear", action="store_true", help="очиска журнала")

args = parser.parse_args()

# основная логика

if args.show:
    logs = eventlog.logger.read_logs()
    formatted_date = None
    if args.date:

        try:
            # Преобразуем введённую дату к нужному формату
            user_date = datetime.strptime(args.date, "%Y-%m-%d")
            formatted_date = user_date.strftime("%d.%m.%Y")  # формат логов
        except ValueError:
            print("❌ Некорректный формат даты. Используй YYYY-MM-DD.")
            sys.exit(1)

    for line in logs:
        parts = line.strip().split(" ", 4)
        message_logs = parts[4] if len(parts) == 5 else ""
        show_line = True

        if args.type and args.type not in line:
            show_line = False
        if args.level and args.level not in line:
            show_line = False
        if args.date and formatted_date and not line.startswith(formatted_date):
            show_line = False
        if args.keyword and args.keyword not in message_logs:
            show_line = False

        if show_line:
            print(line.strip())


if args.add:
    if args.type and args.level and args.message:
        eventlog.logger.log_event(args.type, args.level, args.message)
    else:
        print("❗️Убедитесь, что вы указали --type, --level и --message")
        sys.exit(1)


if args.clear:
    if os.path.isfile("eventlog.log"):
        user_in = input("Вы действительно хотите удалить все записи? [y/N]")
        user_in = user_in.lower()
        if user_in == "y":
            with open("eventlog.log", "w") as file:
                print(" ✅ Журнал очищен.")
        else:
            print("⚠️ Очистка отменена.")
            sys.exit(0)
    else:
        print("⚠️ Журнал ещё не создан.")
