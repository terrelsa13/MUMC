FROM python:3.11

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p mumc_modules/mumc_defaults
RUN mkdir config
RUN mkdir logs

COPY mumc_modules/mumc_defaults/*.yaml mumc_modules/mumc_defaults/
COPY mumc_modules/*.py mumc_modules/
COPY mumc.py .

ENTRYPOINT ["python", "./mumc.py", "-d"]