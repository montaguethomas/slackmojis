FROM python:3-alpine
ARG TARGETPLATFORM
RUN apk upgrade --no-cache
RUN if [[ "linux/arm" == "${TARGETPLATFORM}" ]]; then apk add --no-cache libjpeg-turbo-dev zlib-dev; fi
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /app/
VOLUME /app/storage
ENTRYPOINT ["python3"]
