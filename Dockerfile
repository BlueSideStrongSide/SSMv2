#Dockerfile, Image, Container

FROM python:3.9

COPY sample_script.py .
COPY config ./
COPY src ./

RUN pip install aiohttp asyncio icmplib

CMD ["python", "./sample_script.py"]
