#Dockerfile, Image, Container

#FROM python:3

FROM alpine:latest
# Install Python and pip using apk package manager
RUN apk add --update --no-cache python3 py3-pip

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY sample_script.py .
COPY config/ /config/
COPY src/ /src/

WORKDIR /
ENTRYPOINT ["python", "./sample_script.py"]
