FROM python:3.11

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /config

RUN mkdir -p mumc_modules/

COPY mumc_modules/*.py mumc_modules/
COPY mumc.py .

ENTRYPOINT ["python", "./mumc.py", "-d"]