FROM python:3.9-buster
ENV BOT_NAME=$BOT_NAME

WORKDIR /usr/src/app/"${BOT_NAME:-telegram_bot}"

COPY telegram_bot/requirements.txt /usr/src/app/"${BOT_NAME:-telegram_bot}"
RUN pip install -r /usr/src/app/"${BOT_NAME:-telegram_bot}"/requirements.txt
COPY . /usr/src/app/"${BOT_NAME:-telegram_bot}"
