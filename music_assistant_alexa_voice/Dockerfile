FROM ghcr.io/home-assistant/base-python:3.12-alpine3.24

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY skill ./skill
COPY scripts ./scripts
COPY run.sh /
RUN chmod a+x /run.sh

ENV PORT=5000
EXPOSE 5000

CMD ["/run.sh"]
