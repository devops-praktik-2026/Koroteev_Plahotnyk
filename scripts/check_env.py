#!/usr/bin/env python3
"""Проверка, что на компьютере есть всё нужное для практикума.

Запуск (ничего ставить не нужно, хватит одного Python):

    python3 scripts/check_env.py          Linux и macOS
    python scripts\\check_env.py           Windows

Скрипт ничего не меняет и не устанавливает — только смотрит и рассказывает.
Покажите его вывод преподавателю, если что-то не сходится.
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK, WARN, FAIL = "[ OK ]", "[ !  ]", "[FAIL]"

MIN_PYTHON = (3, 11)
PORTS = {8001: "сервис клиентов", 8002: "сервис заказов", 5432: "база данных"}

problems: list[str] = []
warnings: list[str] = []


def say(marker: str, title: str, detail: str = "") -> None:
    print(f"{marker}  {title}")
    if detail:
        for line in detail.splitlines():
            print(f"        {line}")


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    """Запускает команду и возвращает код возврата и слитый вывод."""
    try:
        done = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return done.returncode, (done.stdout or "") + (done.stderr or "")
    except FileNotFoundError:
        return 127, "команда не найдена"
    except subprocess.TimeoutExpired:
        return 124, "команда не ответила вовремя"


def first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""


# --------------------------------------------------------------------------
# Python
# --------------------------------------------------------------------------
def check_python() -> None:
    version = sys.version_info
    shown = f"{version.major}.{version.minor}.{version.micro}"
    if version >= MIN_PYTHON:
        say(OK, f"Python {shown}")
    else:
        need = ".".join(str(n) for n in MIN_PYTHON)
        say(FAIL, f"Python {shown} — нужен {need} или новее")
        problems.append(f"Обновите Python до {need} или новее")

    # venv нужен для make setup
    try:
        import venv  # noqa: F401

        say(OK, "Модуль venv на месте")
    except ImportError:
        say(FAIL, "Модуль venv отсутствует")
        problems.append("Поставьте пакет для виртуальных окружений: sudo apt install python3-venv")


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------
def check_git() -> None:
    if shutil.which("git") is None:
        say(FAIL, "git не установлен")
        problems.append("Поставьте git — без него вы даже не получите этот проект")
        return

    code, out = run(["git", "--version"])
    say(OK, first_line(out) or "git на месте")

    code, name = run(["git", "config", "--get", "user.name"])
    code2, email = run(["git", "config", "--get", "user.email"])
    if not name.strip() or not email.strip():
        say(WARN, "У git не заполнены имя и почта")
        warnings.append(
            "Выполните:\n"
            '    git config --global user.name "Имя Фамилия"\n'
            '    git config --global user.email "почта@example.com"'
        )
    else:
        say(OK, f"Подпись коммитов: {name.strip()} <{email.strip()}>")


# --------------------------------------------------------------------------
# make
# --------------------------------------------------------------------------
def check_make() -> None:
    if shutil.which("make"):
        code, out = run(["make", "--version"])
        say(OK, first_line(out) or "make на месте")
        return

    if platform.system() == "Windows":
        say(OK, "make не нужен — на Windows его заменяет make.ps1")
        return

    say(WARN, "make не установлен")
    warnings.append(
        "Поставьте make:\n"
        "    Ubuntu/Debian:  sudo apt install make\n"
        "    macOS:          xcode-select --install"
    )


# --------------------------------------------------------------------------
# docker
# --------------------------------------------------------------------------
def check_docker(deep: bool) -> None:
    if shutil.which("docker") is None:
        say(WARN, "docker не установлен — понадобится с занятия 4")
        if platform.system() == "Windows":
            warnings.append(
                "Поставьте Docker Desktop. Контейнеры — это возможность ядра Linux,\n"
                "поэтому на Windows им нужна виртуальная машина: либо WSL 2,\n"
                "либо Hyper-V (он есть в редакциях Pro, Enterprise и Education).\n"
                "На Windows Home остаётся только WSL 2.\n"
                "До занятия 4 это не мешает, но решите вопрос заранее."
            )
        else:
            warnings.append(
                "Поставьте Docker Desktop (macOS) или Docker Engine (Linux). "
                "К занятию 4, но лучше сразу."
            )
        return

    code, out = run(["docker", "--version"])
    say(OK, first_line(out) or "docker на месте")

    code, out = run(["docker", "info"], timeout=25)
    if code != 0:
        say(WARN, "docker установлен, но не запущен")
        warnings.append(
            "Запустите Docker Desktop и дождитесь, пока значок перестанет мигать.\n"
            "На Linux: sudo systemctl start docker\n"
            "До занятия 4 это не мешает."
        )
        return
    say(OK, "docker запущен и отвечает")

    code, out = run(["docker", "compose", "version"])
    if code == 0:
        say(OK, first_line(out) or "docker compose на месте")
    else:
        say(FAIL, "docker compose недоступен")
        problems.append(
            "Нужен docker compose как подкоманда docker. "
            "В Docker Desktop он входит в комплект; на Linux поставьте docker-compose-plugin."
        )

    if deep:
        check_docker_pull()


def check_docker_pull() -> None:
    print()
    print("        Проверяю, скачиваются ли образы (может занять до минуты)…")
    code, out = run(["docker", "pull", "hello-world"], timeout=90)
    if code == 0:
        say(OK, "Образы скачиваются")
        run(["docker", "rmi", "hello-world"], timeout=30)
        return

    say(FAIL, "Образы не скачиваются")
    lowered = out.lower()
    if "403" in out or "forbidden" in lowered or "denied" in lowered:
        problems.append(
            "Похоже на ограничение доступа к хранилищу образов из вашей страны.\n"
            "Пропишите зеркало и перезапустите Docker — см. README,\n"
            "раздел «Если образы не скачиваются»."
        )
    else:
        problems.append(
            f"Не удалось скачать пробный образ. Первая строка ошибки:\n    {first_line(out)}"
        )


# --------------------------------------------------------------------------
# порты
# --------------------------------------------------------------------------
def check_ports() -> None:
    busy = []
    for port, what in PORTS.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.4)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                busy.append((port, what))

    if not busy:
        say(OK, "Порты 8001, 8002 и 5432 свободны")
        return

    listed = ", ".join(f"{port} ({what})" for port, what in busy)
    say(WARN, f"Порты заняты: {listed}")
    warnings.append(
        "Занятые порты не помешают проверкам, но помешают запустить систему.\n"
        "Чаще всего это уже запущенный PostgreSQL на 5432.\n"
        "Освободите порт или поменяйте его в compose.yaml."
    )


# --------------------------------------------------------------------------
# место на диске
# --------------------------------------------------------------------------
def check_disk() -> None:
    free_gb = shutil.disk_usage(os.getcwd()).free / 1024**3
    if free_gb >= 10:
        say(OK, f"Свободно на диске: {free_gb:.0f} ГБ")
    elif free_gb >= 5:
        say(WARN, f"Свободно на диске: {free_gb:.0f} ГБ")
        warnings.append(
            "Образы и данные займут несколько гигабайт. Лучше освободить место заранее."
        )
    else:
        say(FAIL, f"Свободно на диске: {free_gb:.0f} ГБ")
        problems.append("Меньше 5 ГБ свободно — образы не поместятся")


# --------------------------------------------------------------------------
def main() -> int:
    deep = "--docker" in sys.argv or "--full" in sys.argv

    print()
    print("  ПРОВЕРКА ОКРУЖЕНИЯ ДЛЯ ПРАКТИКУМА")
    print(f"  {platform.system()} {platform.release()}, {platform.machine()}")
    print("  " + "-" * 52)
    print()

    check_python()
    print()
    check_git()
    print()
    check_make()
    print()
    check_docker(deep)
    print()
    check_ports()
    check_disk()

    print()
    print("  " + "-" * 52)

    if problems:
        print()
        print(f"  НУЖНО ИСПРАВИТЬ — {len(problems)}:")
        for i, item in enumerate(problems, 1):
            print(f"\n  {i}. {item}")

    if warnings:
        print()
        print(f"  МОЖНО ПОКА ОТЛОЖИТЬ — {len(warnings)}:")
        for i, item in enumerate(warnings, 1):
            print(f"\n  {i}. {item}")

    print()
    if problems:
        print("  Итог: пока запустить не получится. Исправьте пункты выше.")
        print("  Не разобрались — покажите этот вывод преподавателю.")
        return 1

    setup_cmd = ".\\make.ps1 setup" if platform.system() == "Windows" else "make setup"
    deep_cmd = (
        "python scripts\\check_env.py --docker"
        if platform.system() == "Windows"
        else "python3 scripts/check_env.py --docker"
    )

    if warnings:
        print("  Итог: основное на месте, часть вещей понадобится позже.")
        print(f"  Можно выполнять: {setup_cmd}")
        return 0

    print(f"  Итог: всё на месте. Выполняйте: {setup_cmd}")
    if not deep:
        print()
        print("  Проверить ещё и скачивание образов:")
        print(f"      {deep_cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
