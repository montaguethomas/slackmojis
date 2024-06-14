FROM python:3-alpine
ARG TARGETPLATFORM
RUN apk upgrade --no-cache
RUN [[ "linux/arm" == "${TARGETPLATFORM}" ]] && apk add --no-cache libjpeg-turbo-dev zlib-dev
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /app/
VOLUME /app/storage
ENTRYPOINT ["python3"]
