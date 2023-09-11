FROM python:3.10-slim

#
LABEL maintainer="mkhaikin@yandex.ru"

#
WORKDIR /src

#
COPY . .

#
RUN apt update && \
    apt install -y --no-install-recommends git && \
    git init . && \
    pip install --no-cache-dir --upgrade -r /src/requirements.txt
#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

#
CMD ["uvicorn", "app.main:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
