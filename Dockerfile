FROM python:3.10

ARG SETTINGS_MODULE=submitter.settings.prod_settings

EXPOSE 8000

WORKDIR /app

COPY requirements.txt /app/

RUN ["pip", "install", "-r", "requirements.txt"]
RUN ["pip", "install", "daphne"]

COPY . /app/

# TODO: change to prod_settings after test
ENV DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]