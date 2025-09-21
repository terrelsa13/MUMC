FROM docker.io/library/python:3.13-slim

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p mumc_modules/mumc_defaults
RUN mkdir config
RUN mkdir logs

COPY mumc_modules/mumc_defaults/*.yaml mumc_modules/mumc_defaults/
COPY mumc_modules/*.py mumc_modules/
COPY mumc.py .

USER nobody:nogroup

ENTRYPOINT ["python", "./mumc.py"]
