# Aetheris Deployment Guide

## 1. Prerequisites
* Python 3.10+
* Virtual Environment or Docker installed
* Git

## 2. Installation
```bash
git clone https://github.com/msitarzewski/agency-agents.git
cd agency-agents/aetheris
pip install -r requirements.txt
```

## 3. Running via Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV PYTHONPATH=src
ENTRYPOINT ["python", "src/kernel/core.py"]
```
Build and run:
```bash
docker build -t aetheris-os .
docker run -v ${PWD}:/app/workspace aetheris-os --goal "Build web service"
```
