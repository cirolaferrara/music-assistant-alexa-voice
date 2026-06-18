# Music Assistant Alexa Voice Skill

Voice-control [Music Assistant](https://music-assistant.io) from Alexa. This skill searches your MA library/providers and starts playback on your existing MA players (Satellite, RackPi, Sonos, etc.).

## Home Assistant add-on (recommended)

This repository is a Home Assistant add-on repository. Install it directly in Supervisor:

1. **Settings → Add-ons → Add-on Store → ⋮ → Custom repositories**
2. Add: `https://github.com/sickkick/music-assistant-alexa-voice`
3. Install **Music Assistant Alexa Voice**
4. Configure `ma_token`, `default_player_id`, and verify `ma_url`
5. Start the add-on and open **Open Web UI** to test `/players`

See [music_assistant_alexa_voice/DOCS.md](music_assistant_alexa_voice/DOCS.md) for full add-on setup and troubleshooting.

## Example utterances

- "Alexa, open music assistant"
- "Alexa, ask music assistant to play Fleetwood Mac"
- "Alexa, ask music assistant to play jazz in the kitchen"
- "Alexa, ask music assistant to pause"
- "Alexa, ask music assistant to skip"

## Architecture

```mermaid
flowchart LR
  Echo[Alexa Device] -->|HTTPS| Proxy[Reverse Proxy]
  Proxy --> Skill[HA Add-on / Docker Service]
  Skill -->|HTTP JSON-RPC| MA[Music Assistant API]
  MA --> Player[MA Player]
```

## Standalone Docker

You can also run outside Home Assistant:

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:5055/health
```

Edit `.env`:

| Variable | Description |
|---|---|
| `MA_URL` | Music Assistant base URL, e.g. `http://192.168.1.10:8095` |
| `MA_TOKEN` | MA API bearer token |
| `DEFAULT_PLAYER_ID` | Player ID to use when no room is specified |
| `PLAYER_ALIASES` | Optional JSON map of friendly names → player IDs |

Find player IDs:

```bash
docker compose run --rm music-assistant-alexa-voice python scripts/list_players.py
```

Or visit `http://localhost:5055/players`.

## Expose HTTPS for Alexa

Alexa requires a public HTTPS endpoint. Example with Cloudflare Tunnel:

```yaml
ingress:
  - hostname: alexa-voice.example.com
    service: http://homeassistant.local:5000
```

Your Alexa skill endpoint:

```text
https://alexa-voice.example.com/alexa
```

## Create the Alexa skill

1. Open the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. **Create Skill** → Custom → Provision your own
3. Import `music_assistant_alexa_voice/skill/interaction-model/en-US.json`
4. Invocation name: `music assistant`
5. Endpoint: your public HTTPS URL + `/alexa`

## Supported commands

| Voice command | MA API action |
|---|---|
| play {query} | `music/search` → `player_queues/play_media` |
| play {query} in {room} | resolves player → play |
| pause | `player_queues/pause` |
| resume | `player_queues/play` |
| stop / cancel | `player_queues/stop` |
| next / skip | `player_queues/next` |
| previous / go back | `player_queues/previous` |

## Project layout

```text
repository.yaml
music_assistant_alexa_voice/
  config.yaml        Home Assistant add-on metadata
  Dockerfile
  run.sh
  DOCS.md
  app/               Flask service
  skill/             Alexa interaction model
  scripts/
docker-compose.yml   Standalone Docker option
```

## Notes

- This skill controls MA players directly. It does **not** stream audio to the Echo speaker itself.
- For Echo-as-speaker streaming, see the official [Music Assistant Alexa player docs](https://www.music-assistant.io/player-support/alexa/).
