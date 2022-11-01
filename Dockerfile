#Dockerfile, Image, Container

FROM python:3.9

COPY sample_script.py .
COPY config ./
COPY src ./
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["python", "./sample_script.py"]
