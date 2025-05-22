FROM python:3.13-alpine3.21
RUN ln -s /usr/share/zoneinfo/America/Santiago /etc/localtime
ENV PYTHONUNBUFFERED=x
WORKDIR /app/
CMD ["sh", "-c", "apk upgrade --cache-max-age 60 tzdata && exec ./ntpcl.py"]
