import argparse  # Модуль для обработки аргументов командной строки
import os  # Работа с файловой системой
import sys  # Для завершения программы
from argparse import RawTextHelpFormatter  # Форматирование справки
from datetime import datetime  # Работа с датой/временем

import eventlog.logger  # Внутренний модуль с логикой логирования
from colorama import Fore, Style, init  # Цветной вывод в терминал

init(autoreset=True)  # Автоматически сбрасывать цвет после каждой строки

# ─────────────── Инициализация парсера с описанием ───────────────
parser = argparse.ArgumentParser(
    description="""\
Утилита для ведения журнала событий.

📌 Команды:
  add     — добавить запись в лог
  show    — отфильтрованный просмотр журнала
  clear   — очистка журнала

📋 Примеры:
  python main.py add -t SYSTEM -l ERROR -m "Сбой в системе"
  python main.py show --level WARNING
  python main.py clear
""",
    formatter_class=RawTextHelpFormatter,
)

subparsers = parser.add_subparsers(dest="command", required=True)

# ─────────────── Команда add ───────────────
add_parser = subparsers.add_parser("add", help="Добавить запись в лог")
group_add = add_parser.add_argument_group("команда добавить")
group_add.add_argument(
    "-t",
    "--type",
    choices=["SYSTEM", "USER", "APP"],
    metavar="TYPE",
    help="Тип события",
)
group_add.add_argument(
    "-l",
    "--level",
    choices=["INFO", "WARNING", "ERROR"],
    metavar="LEVEL",
    help="Уровень",
)
group_add.add_argument("-m", "--message", type=str, help="Основной текст события")

# ─────────────── Команда show ───────────────
show_parser = subparsers.add_parser("show", help="Показать лог")
group_show = show_parser.add_argument_group("команда показать")
group_show.add_argument(
    "-t",
    "--type",
    choices=["SYSTEM", "USER", "APP"],
    metavar="TYPE",
    help="Тип события",
)
group_show.add_argument(
    "-l",
    "--level",
    choices=["INFO", "WARNING", "ERROR"],
    metavar="LEVEL",
    help="Уровень",
)
group_show.add_argument(
    "-d", "--date", type=str, help="Дата события (формат: YYYY-MM-DD)"
)
group_show.add_argument("-k", "--keyword", type=str, help="Фильтр по ключевому слову")

# ─────────────── Команда clear ───────────────
clear_parser = subparsers.add_parser("clear", help="Очистить лог")

# ─────────────── Обработка аргументов ───────────────
args = parser.parse_args()

# ─────────────── Команда show ───────────────
if args.command == "show":
    logs = eventlog.logger.read_logs()
    formatted_date = None

    if args.date:
        try:
            user_date = datetime.strptime(args.date, "%Y-%m-%d")
            formatted_date = user_date.strftime("%d.%m.%Y")
        except ValueError:
            print("❌ Некорректный формат даты. Используй YYYY-MM-DD.")
            sys.exit(1)

    for line in logs:
        parts = line.strip().split(" ", 4)
        date = parts[0]
        time = parts[1]
        event_type = parts[2]
        level = parts[3]
        message_logs = parts[4] if len(parts) == 5 else ""

        # Цвет по уровню
        if level == "INFO":
            level_colored = Fore.GREEN + level + Style.RESET_ALL
        elif level == "WARNING":
            level_colored = Fore.YELLOW + level + Style.RESET_ALL
        elif level == "ERROR":
            level_colored = Fore.RED + level + Style.RESET_ALL
        else:
            level_colored = level

        timestamp = f"{date} {time}"
        show_line = True

        if args.type and args.type != event_type:
            show_line = False
        if args.level and args.level != level:
            show_line = False
        if args.date and formatted_date != date:
            show_line = False
        if args.keyword and args.keyword not in message_logs:
            show_line = False

        if show_line:
            print(
                f"[{timestamp}] [{event_type:<8}] [{level_colored:<8}] {message_logs}"
            )

# ─────────────── Команда add ───────────────
elif args.command == "add":
    if args.type and args.level and args.message:
        eventlog.logger.log_event(args.type, args.level, args.message)
    else:
        print("❗ Укажите --type, --level и --message")
        sys.exit(1)

# ─────────────── Команда clear ───────────────
elif args.command == "clear":
    if os.path.isfile("eventlog.log"):
        user_in = input("Вы действительно хотите удалить все записи? [y/N] ").lower()
        if user_in == "y":
            with open("eventlog.log", "w"):
                print("✅ Журнал очищен.")
        else:
            print("⚠️ Очистка отменена.")
            sys.exit(0)
    else:
        print("⚠️ Журнал ещё не создан.")
