# Project Context

Last updated: 2026-06-18

This document captures the current state, architecture, and setup decisions for **music-assistant-alexa-voice** so future work (human or agent) can continue without re-discovering context.

## Goal

Voice-control **Music Assistant** from Alexa on existing MA players (Satellite, RackPi, Sonos, etc.). This does **not** stream audio to Echo speakers — it searches MA and starts playback on configured players.

Example: *"Alexa, ask music assistant to play Fleetwood Mac in the kitchen"*

## Repository

- **GitHub:** https://github.com/sickkick/music-assistant-alexa-voice
- **Branch:** `cursor/music-assistant-alexa-voice-skill`
- **Owner GitHub:** sickkick
- **Owner HA:** Music Assistant installed (Home Assistant add-on), players include Sat1 / Satellite / RackPi / OfficePi

## Architecture

```text
Alexa Device
  → HTTPS (Home Assistant Cloud / Nabu Casa)
  → HA custom integration proxy  /api/music_assistant_alexa_voice/alexa
  → Add-on Flask service         /alexa
  → Music Assistant HTTP API     /api (JSON-RPC)
  → MA player playback
```

### Why a custom integration + add-on?

- The **add-on** runs the Alexa skill logic and talks to Music Assistant internally.
- **Home Assistant webhooks** cannot return custom JSON responses (Alexa requires synchronous Alexa Skill JSON).
- **Home Assistant Cloud** exposes HA’s HTTP API via `https://YOUR_ID.ui.nabu.casa`, not arbitrary add-on ports.
- The **custom integration** registers an unauthenticated (token-gated) HTTP view that proxies POST bodies to the add-on and returns the Alexa response.

### Alternative paths (not primary)

- **Self-hosted HTTPS** → point reverse proxy at add-on `:5000/alexa` or standalone Docker on `:5055`
- **Echo-as-speaker streaming** → different project; see [official MA Alexa docs](https://www.music-assistant.io/player-support/alexa/)

## Repo layout

```text
repository.yaml                              # HA add-on repo metadata
music_assistant_alexa_voice/                 # Supervisor add-on
  config.yaml
  Dockerfile
  run.sh                                     # bashio → reads /data/options.json
  DOCS.md                                    # Add-on documentation tab
  app/                                       # Flask service
    app.py
    config.py                                # env + /data/options.json
    ma_client.py                             # MA HTTP JSON-RPC client
    skill/
      alexa.py
      router.py
  skill/interaction-model/en-US.json
  scripts/list_players.py
custom_components/music_assistant_alexa_voice/  # HA Cloud proxy integration
  manifest.json
  config_flow.py
  http.py                                    # AlexaSkillView proxy
  strings.json
hacs.json
docker-compose.yml                           # Standalone Docker (root Dockerfile)
Dockerfile                                   # Standalone build (no bashio)
README.md
```

## Home Assistant add-on

### Install

1. Settings → Add-ons → Add-on Store → ⋮ → Custom repositories
2. Add: `https://github.com/sickkick/music-assistant-alexa-voice`
3. Install **Music Assistant Alexa Voice**

### Add-on options

| Option | Purpose |
|---|---|
| `ma_url` | Internal MA API URL (default `http://08524bff_music_assistant:8095`) |
| `ma_token` | MA API bearer token |
| `default_player_id` | Default MA player queue ID |
| `player_aliases` | JSON map of room names → player IDs |
| `port` | Internal HTTP port (default 5000) |

### Add-on notes

- Uses **ingress** for Web UI (`/players` health/debug); host port 5000 is **not** exposed by default.
- `run.sh` reads Supervisor options via bashio from `/data/options.json`.
- Internal add-on hostname: `http://music_assistant_alexa_voice:5000`

## Home Assistant Cloud setup (recommended)

### Prerequisites

- Active **Home Assistant Cloud (Nabu Casa)** subscription with Remote Access enabled
- Add-on running and healthy (`/health` returns ok)

### Custom integration

1. Copy `custom_components/music_assistant_alexa_voice` → HA `config/custom_components/` (or HACS)
2. Restart Home Assistant
3. Settings → Devices & Services → Add Integration → **Music Assistant Alexa Voice**
4. Configure:
   - **Add-on URL:** `http://music_assistant_alexa_voice:5000`
   - **Cloud access token:** long random secret (user-defined)

### Alexa skill HTTPS endpoint

```text
https://YOUR_ID.ui.nabu.casa/api/music_assistant_alexa_voice/alexa?token=YOUR_CLOUD_ACCESS_TOKEN
```

- Set this in Alexa Developer Console → Build → Endpoint → HTTPS
- Certificate: Amazon trust (wildcard/subdomain for `*.ui.nabu.casa`)
- Interaction model: `music_assistant_alexa_voice/skill/interaction-model/en-US.json`
- Invocation name: `music assistant`

## Music Assistant API commands used

| Voice intent | MA command |
|---|---|
| Play query | `music/search` → `player_queues/play_media` |
| Pause | `player_queues/pause` |
| Resume | `player_queues/play` |
| Stop | `player_queues/stop` |
| Next | `player_queues/next` |
| Previous | `player_queues/previous` |

Search priority: track → album → playlist → artist (artist uses `radio_mode: true`).

## Standalone Docker (optional)

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:5055/health
```

Uses root `Dockerfile` (gunicorn directly, no bashio). Not required when running as HA add-on.

## Git / commit conventions

- Use conventional commits (`feat`, `fix`, `docs`, etc.)
- Branch prefix: `cursor/`
- **Do not** include `Co-authored-by: Cursor` in commits — use `git commit-tree` if Cursor injects co-author trailers

## User environment (from discovery)

- Music Assistant installed in Home Assistant (beta/stable update entities present)
- Existing MA voice script: `script.llm_script_for_music_assistant_voice_requests` (blueprint-based)
- Example default player in LLM script: `media_player.satellite1_407a08_sat1_media_player_2` (Sat1)
- No Alexa `media_player` entities in HA at time of setup (voice-control targets MA players, not Echo)
- Docker daemon was not running on dev Mac during initial build test

## Open / follow-up items

- [ ] User to configure `ma_token`, `default_player_id`, and integration cloud token in production HA
- [ ] User to create Alexa skill in Developer Console and point endpoint at Nabu Casa URL
- [ ] Optionally publish integration via HACS default repo
- [ ] Optionally merge branch to `main` and set default branch on GitHub
- [ ] Test end-to-end: Alexa utterance → Cloud → integration → add-on → MA → player

## Key files to read first

1. `README.md` — user-facing overview
2. `music_assistant_alexa_voice/DOCS.md` — add-on + Cloud setup
3. `custom_components/music_assistant_alexa_voice/http.py` — Cloud proxy
4. `music_assistant_alexa_voice/app/skill/router.py` — Alexa intent handling
5. `music_assistant_alexa_voice/app/ma_client.py` — MA API client
