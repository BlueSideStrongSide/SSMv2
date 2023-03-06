#Dockerfile, Image, Container

FROM python:3

COPY sample_script.py .
COPY requirements.txt .
COPY config/ /config/
COPY src/ /src/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
WORKDIR /
ENTRYPOINT ["python", "./sample_script.py"]
