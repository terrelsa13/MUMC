FROM python:alpine3.14

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /media-cleaner/requirements.txt

WORKDIR /media-cleaner

RUN pip install -r requirements.txt

COPY . . 

RUN chmod a+x media_cleaner.py
RUN chmod a+x media_cleaner_config.py
RUN chmod 0644 crontab

RUN crontab crontab
CMD ["crond", "-f"]