#Dockerfile, Image, Container

FROM python:3

COPY sample_script.py .
COPY config/ /config/
COPY src/ /src/
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
WORKDIR /
CMD ["python", "./sample_script.py"]
