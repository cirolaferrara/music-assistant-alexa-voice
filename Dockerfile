# Standalone Docker build (same image as the Home Assistant add-on)
FROM ghcr.io/home-assistant/base-python:3.12-alpine3.24

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY music_assistant_alexa_voice/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY music_assistant_alexa_voice/app ./app
COPY music_assistant_alexa_voice/skill ./skill
COPY music_assistant_alexa_voice/scripts ./scripts

ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "60", "app.app:app"]
