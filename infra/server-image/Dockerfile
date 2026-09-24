# Образ учебного «сервера».
# Внутри — обычная Debian, ssh для входа и надзиратель, который следит за службами.
# Ansible подключается сюда по-настоящему: по сети, по ключу, как к серверу.
#
# Собирается автоматически при создании стенда. Вручную:
#     docker build -t praktikum-server infra/server-image

FROM debian:12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openssh-server \
        python3 \
        python3-venv \
        python3-pip \
        supervisor \
        sudo \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Каталог, который нужен ssh для работы
RUN mkdir -p /run/sshd

# Пользователь, под которым будет работать приложение.
# Дальше всё остальное — каталоги, зависимости, службу — настраивает
# сценарий Ansible. Здесь только минимум, чтобы можно было войти.
RUN useradd --create-home --shell /bin/bash deploy \
    && echo 'deploy ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/deploy \
    && mkdir -p /home/deploy/.ssh \
    && chmod 700 /home/deploy/.ssh \
    && chown -R deploy:deploy /home/deploy/.ssh

# Открытый ключ пары кладётся при создании стенда
ARG SSH_PUBLIC_KEY=""
RUN if [ -n "$SSH_PUBLIC_KEY" ]; then \
        echo "$SSH_PUBLIC_KEY" > /home/deploy/.ssh/authorized_keys \
        && chmod 600 /home/deploy/.ssh/authorized_keys \
        && chown deploy:deploy /home/deploy/.ssh/authorized_keys; \
    fi

# Вход только по ключу — то же правило, что на настоящем сервере
RUN sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22

# Надзиратель запускает ssh, а позже — вашу службу приложения.
COPY supervisord.conf /etc/supervisor/conf.d/server.conf

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
