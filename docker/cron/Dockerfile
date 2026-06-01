FROM alpine:3.23

RUN apk add --no-cache docker-cli busybox-suid

COPY start.sh /start.sh

RUN chmod +x /start.sh