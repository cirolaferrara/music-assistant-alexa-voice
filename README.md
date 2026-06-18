# Music Assistant Alexa Voice Skill

Voice-control [Music Assistant](https://music-assistant.io) from Alexa. This skill searches your MA library/providers and starts playback on your existing MA players (Satellite, RackPi, Sonos, etc.).

Example utterances:

- "Alexa, open music assistant"
- "Alexa, ask music assistant to play Fleetwood Mac"
- "Alexa, ask music assistant to play jazz in the kitchen"
- "Alexa, ask music assistant to pause"
- "Alexa, ask music assistant to skip"

## Architecture

```mermaid
flowchart LR
  Echo[Alexa Device] -->|HTTPS| Proxy[Reverse Proxy]
  Proxy --> Skill[This Docker Service]
  Skill -->|HTTP JSON-RPC| MA[Music Assistant API]
  MA --> Player[MA Player]
```

Alexa sends voice requests to your public HTTPS endpoint. This service translates them into Music Assistant API commands (`music/search`, `player_queues/play_media`, etc.).

## Prerequisites

1. Music Assistant running (Home Assistant add-on is fine)
2. A Music Assistant API token (Settings → User management → API tokens)
3. An [Amazon Developer account](https://developer.amazon.com/)
4. A public HTTPS URL pointing at this service (Cloudflare Tunnel, Caddy, Nginx, etc.)

## Quick start

### 1. Configure environment

```bash
cp .env.example .env
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

Or start the container and visit `http://localhost:5055/players`.

### 2. Run with Docker

```bash
docker compose up -d --build
```

Health check:

```bash
curl http://localhost:5055/health
```

### 3. Expose HTTPS

Alexa requires a public HTTPS endpoint. Example with Cloudflare Tunnel:

```yaml
# cloudflared config snippet
ingress:
  - hostname: alexa-voice.example.com
    service: http://localhost:5055
```

Your Alexa skill endpoint will be:

```text
https://alexa-voice.example.com/alexa
```

### 4. Create the Alexa skill

1. Open the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. **Create Skill**
   - Name: `Music Assistant Voice`
   - Model: **Custom**
   - Hosting: **Provision your own**
3. **Build → Interaction Model**
   - Invocation name: `music assistant`
   - Import `skill/interaction-model/en-US.json` (JSON Editor → Import)
   - Build the model
4. **Build → Endpoint**
   - Type: **HTTPS**
   - URL: `https://alexa-voice.example.com/alexa`
   - Certificate: Amazon trust (or your cert type as appropriate)
5. **Test**
   - Enable testing in **Development**
   - Try: *open music assistant* then *play radiohead*

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

Search priority: track → album → playlist → artist (artist uses radio mode).

## Player aliases

Map Alexa room names to MA player IDs:

```env
PLAYER_ALIASES={"kitchen":"abc123","office":"def456","satellite":"ghi789"}
```

If no alias matches, the service fuzzy-matches against MA player display names.

## Local testing

Simulate an Alexa intent:

```bash
curl -s http://localhost:5055/alexa \
  -H 'Content-Type: application/json' \
  -d '{
    "version": "1.0",
    "session": {"attributes": {}},
    "request": {
      "type": "IntentRequest",
      "intent": {
        "name": "PlayMusicIntent",
        "slots": {
          "Query": {"name": "Query", "value": "fleetwood mac"}
        }
      }
    }
  }'
```

## Troubleshooting

| Issue | Fix |
|---|---|
| `MA_TOKEN is required` | Fill in `.env` before starting the container |
| Cannot reach MA from Docker | Set `MA_URL` to your LAN IP, not `localhost`. On Linux Docker, `host.docker.internal` may not work — use the HA host IP |
| Player not found | Run `/players` and copy the exact `player_id` into `DEFAULT_PLAYER_ID` or `PLAYER_ALIASES` |
| Alexa can't reach skill | Confirm HTTPS works externally and the endpoint path is `/alexa` |
| No search results | Verify the query works in the MA UI first; provider accounts must be linked in MA |

## Notes

- This skill controls MA players directly. It does **not** stream audio to the Echo speaker itself.
- For Echo-as-speaker streaming, see the official [Music Assistant Alexa player docs](https://www.music-assistant.io/player-support/alexa/).
- The active player is remembered in the Alexa session, so pause/next/stop apply to the last player you played on.

## Project layout

```text
app/
  app.py           Flask entrypoint
  config.py        Environment settings
  ma_client.py     Music Assistant API client
  skill/
    alexa.py       Alexa response helpers
    router.py      Intent routing
skill/
  interaction-model/en-US.json
scripts/
  list_players.py
```
