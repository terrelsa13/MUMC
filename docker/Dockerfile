FROM python:3.11

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /config/logs

VOLUME /config

COPY mumc_config_defaults.py .
COPY mumc.py .

ENTRYPOINT ["python", "./mumc.py"]