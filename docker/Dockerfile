FROM python:3.11

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /config /logs
#VOLUME config/ logs/
#VOLUME /logs

RUN mkdir -p mumc_modules/mumc_defaults/
#RUN mkdir config/
#RUN mkdir logs/

#RUN touch config/mumc_config.yaml
#RUN touch logs/mumc_DEBUG.log
#RUN touch logs/mumc_CRON_OUTPUT.log

COPY mumc_modules/*.py mumc_modules/
COPY mumc_modules/mumc_defaults/*.yaml mumc_modules/mumc_defaults/
COPY mumc.py .

ENTRYPOINT ["python", "./mumc.py", "-d"]