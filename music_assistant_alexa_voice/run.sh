#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
set -e

bashio::log.info "Starting Music Assistant Alexa Voice"

if [ -f /data/options.json ]; then
  export MA_URL="$(bashio::config 'ma_url')"
  export MA_TOKEN="$(bashio::config 'ma_token')"
  export DEFAULT_PLAYER_ID="$(bashio::config 'default_player_id')"
  export PLAYER_ALIASES="$(bashio::config 'player_aliases')"
  export PORT="$(bashio::config 'port')"
else
  export MA_URL="${MA_URL:-http://08524bff_music_assistant:8095}"
  export MA_TOKEN="${MA_TOKEN:-}"
  export DEFAULT_PLAYER_ID="${DEFAULT_PLAYER_ID:-}"
  export PLAYER_ALIASES="${PLAYER_ALIASES:-{}}"
  export PORT="${PORT:-5000}"
fi

if [ -z "${MA_TOKEN}" ]; then
  bashio::log.error "ma_token is required. Create one in Music Assistant -> Settings -> User management -> API tokens."
  exit 1
fi

if [ -z "${DEFAULT_PLAYER_ID}" ]; then
  bashio::log.error "default_player_id is required. Open the add-on /players page after starting to find player IDs."
  exit 1
fi

bashio::log.info "Using Music Assistant at ${MA_URL} on port ${PORT}"

exec gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers 1 \
  --threads 4 \
  --timeout 60 \
  app.app:app
