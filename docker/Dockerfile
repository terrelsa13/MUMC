FROM python:3.11

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#VOLUME /usr/src/app/config /usr/src/app/logs
VOLUME /user/src/app/config
#VOLUME /logs

RUN mkdir -p /usr/src/app/mumc_modules/mumc_defaults/
#RUN mkdir /usr/src/app/config/
#RUN mkdir /usr/src/app/logs/

#RUN touch /usr/src/app/config/mumc_config.yaml
#RUN touch /usr/src/app/logs/mumc_DEBUG.log
#RUN touch logs/mumc_CRON_OUTPUT.log

COPY mumc_modules/*.py mumc_modules/
COPY mumc_modules/mumc_defaults/*.yaml mumc_modules/mumc_defaults/
COPY mumc.py .

ENTRYPOINT ["python", "./mumc.py", "-d"]