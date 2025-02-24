FROM python:3.11

WORKDIR /usr/src/app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /config

RUN mkdir -p mumc_modules/
RUN mkdir -p config/
RUN mkdir -p logs/
#RUN usermod -aG docker $USER
#RUN systemctl restart docker

COPY mumc_modules/docker_templates/mumc_template_config.yaml config/mumc_config.yaml
COPY mumc_modules/docker_templates/mumc_template_DEBUG.txt logs/mumc_DEBUG.log
COPY mumc_modules/docker_templates/mumc_template_CRONOUTPUT.txt logs/mumc_CRON_OUTPUT.log
COPY mumc_modules/*.py mumc_modules/
COPY mumc.py .

ENTRYPOINT ["python", "./mumc.py", "-d"]