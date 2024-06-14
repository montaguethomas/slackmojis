FROM python:3-alpine
RUN apk upgrade --no-cache && apk add --no-cache zlib-dev
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /app/
VOLUME /app/storage
ENTRYPOINT ["python3"]
