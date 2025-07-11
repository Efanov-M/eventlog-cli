import argparse  # Модуль для обработки аргументов командной строки
import os  # Модуль для работы с файловой системой
import sys  # Модуль для принудительного завершения программы
from datetime import datetime  # Работа с датой и временем

import eventlog.logger  # Собственный модуль для логики записи/чтения логов
from colorama import Fore, Style, init  # Цветной вывод в консоль

init(autoreset=True)  # Автоматически сбрасывает цвет после каждой строки (важно!)

# Основной парсер командной строки
parser = argparse.ArgumentParser(description="Утилита для ведения журнала событий ")

# Создаём подкоманды: add, show, clear
subparsers = parser.add_subparsers(dest="command", required=True)

# ─────────────── Подкоманда add ───────────────
add_parser = subparsers.add_parser("add", help="Добавить запись в лог")

# Добавляем аргумент --type или -t
add_parser.add_argument(
    "-t",
    "--type",
    choices=["SYSTEM", "USER", "APP"],
    metavar="TYPE",
    help="Тип события: SYSTEM | USER | APP",
)

# Аргумент уровня важности (например, INFO, ERROR)
add_parser.add_argument(
    "-l",
    "--level",
    choices=["INFO", "WARNING", "ERROR"],
    metavar="LEVEL",
    help="Уровень важности: INFO | WARNING | ERROR",
)

# Аргумент сообщения — обязательный текст
add_parser.add_argument("-m", "--message", type=str, help="Основной текст события")

# ─────────────── Подкоманда show ───────────────
show_parser = subparsers.add_parser("show", help="Показать лог")

# Фильтрация по типу события
show_parser.add_argument(
    "-t",
    "--type",
    choices=["SYSTEM", "USER", "APP"],
    metavar="TYPE",
    help="Тип события: SYSTEM | USER | APP",
)

# Фильтрация по уровню
show_parser.add_argument(
    "-l",
    "--level",
    choices=["INFO", "WARNING", "ERROR"],
    metavar="LEVEL",
    help="Уровень важности: INFO | WARNING | ERROR",
)

# Фильтрация по дате в формате YYYY-MM-DD
show_parser.add_argument(
    "-d", "--date", type=str, help="Дата события (формат: YYYY-MM-DD)"
)

# Поиск по ключевому слову в сообщении
show_parser.add_argument(
    "-k", "--keyword", type=str, help="Фильтр по ключевому слову в тексте сообщения"
)

# ─────────────── Подкоманда clear ───────────────
clear_parser = subparsers.add_parser("clear", help="Очистить лог")

# ─────────────── Получение аргументов ───────────────
args = parser.parse_args()  # Сохраняем все введённые аргументы в объект args

# ─────────────── Логика команды show ───────────────
if args.command == "show":
    logs = eventlog.logger.read_logs()  # Считываем строки из лог-файла
    formatted_date = None

    # Если указана дата, преобразуем её в формат из логов
    if args.date:
        try:
            user_date = datetime.strptime(
                args.date, "%Y-%m-%d"
            )  # преобразуем в объект datetime
            formatted_date = user_date.strftime("%d.%m.%Y")  # формат логов: DD.MM.YYYY
        except ValueError:
            print("❌ Некорректный формат даты. Используй YYYY-MM-DD.")
            sys.exit(1)

    for line in logs:
        parts = line.strip().split(
            " ", 4
        )  # Разбиваем строку на части: дата, время, тип, уровень, сообщение

        date = parts[0]
        time = parts[1]
        event_type = parts[2]
        level = parts[3]
        message_logs = parts[4] if len(parts) == 5 else ""

        # Добавляем цвет к уровню важности
        if level == "INFO":
            level_colored = Fore.GREEN + level + Style.RESET_ALL
        elif level == "WARNING":
            level_colored = Fore.YELLOW + level + Style.RESET_ALL
        elif level == "ERROR":
            level_colored = Fore.RED + level + Style.RESET_ALL
        else:
            level_colored = level  # fallback (на всякий случай)

        timestamp = f"{date} {time}"  # Собираем полную метку времени

        show_line = True  # По умолчанию строка отображается

        # Применяем фильтры (если заданы)
        if args.type and args.type not in line:
            show_line = False
        if args.level and args.level not in line:
            show_line = False
        if args.date and formatted_date and not line.startswith(formatted_date):
            show_line = False
        if args.keyword and args.keyword not in message_logs:
            show_line = False

        # Если строка прошла все фильтры — выводим её
        if show_line:
            print(
                f"[{timestamp}] [{event_type:<8}] [{level_colored:<8}] {message_logs}"
            )

# ─────────────── Логика команды add ───────────────
if args.command == "add":
    if args.type and args.level and args.message:
        # Запись события в лог-файл
        eventlog.logger.log_event(args.type, args.level, args.message)
    else:
        print("❗️Убедитесь, что вы указали --type, --level и --message")
        sys.exit(1)

# ─────────────── Логика команды clear ───────────────
if args.command == "clear":
    # Проверка: существует ли лог-файл
    if os.path.isfile("eventlog.log"):
        user_in = input("Вы действительно хотите удалить все записи? [y/N]")
        user_in = user_in.lower()
        if user_in == "y":
            # Очищаем лог-файл (перезаписываем пустым содержимым)
            with open("eventlog.log", "w") as file:
                print(" ✅ Журнал очищен.")
        else:
            print("⚠️ Очистка отменена.")
            sys.exit(0)
    else:
        print("⚠️ Журнал ещё не создан.")
