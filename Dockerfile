FROM python:3.10-slim

#
LABEL maintainer="mkhaikin@yandex.ru"

#
WORKDIR /project

#
COPY src requirements.txt ./src/

#
RUN apt update && \
    apt install -y --no-install-recommends git && \
    git init . && \
    pip install --no-cache-dir --upgrade -r ./src/requirements.txt && \
    rm ./src/requirements.txt && \
    pip install pre-commit && \
    cp src/api/v1/services/exam.yaml ./.pre-commit-config.yaml && \
    pre-commit install --install-hooks

#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

#
CMD ["uvicorn", "api:fastapi_app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
