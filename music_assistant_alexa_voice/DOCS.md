# Music Assistant Alexa Voice

Voice-control [Music Assistant](https://music-assistant.io) players from Alexa.

## Home Assistant add-on (recommended)

### Install

1. In Home Assistant, open **Settings → Add-ons → Add-on Store → ⋮ → Custom repositories**
2. Add this repository URL:

   ```text
   https://github.com/Shaffer-Softworks/music-assistant-alexa-voice
   ```

3. Refresh the add-on store and install **Music Assistant Alexa Voice**
4. Configure the add-on:

   | Option | Description |
   |---|---|
   | **Music Assistant URL** | Internal MA API URL. Default `http://d5369777-music-assistant:8095` matches the official Music Assistant app hostname (hyphenated). If yours differs, open the Music Assistant app **Info** page and use `http://<hostname>:8095`. |
   | **Music Assistant API token** | Create in MA → Settings → User management → API tokens |
   | **Default player ID** | Player ID from MA → Settings → Players |
   | **Player aliases** | Optional JSON map, e.g. `{"kitchen":"player-id","satellite":"other-id"}` |

5. Start the add-on
6. Open the add-on **Open Web UI** link to verify MA connectivity and copy player IDs (JSON also available at `players`)

## Home Assistant Cloud (recommended for Alexa)

Alexa needs a public HTTPS endpoint. The easiest way with Home Assistant is **Home Assistant Cloud (Nabu Casa)** plus the included custom integration proxy.

Home Assistant webhooks cannot return Alexa's JSON response, so this project ships a small integration that exposes a synchronous proxy endpoint through Home Assistant itself. That endpoint is reachable remotely through your Nabu Casa URL.

### 1. Enable Home Assistant Cloud

1. Open **Settings → Home Assistant Cloud**
2. Sign in and enable **Remote Access**

Your remote URL looks like:

```text
https://abcdef12.ui.nabu.casa
```

### 2. Install the custom integration

Choose one:

**Option A — HACS (recommended)**

1. Add this repository as a custom HACS integration repository, or copy `custom_components/music_assistant_alexa_voice` into your `config/custom_components/` folder
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for **Music Assistant Alexa Voice**

**Option B — Manual copy**

1. Copy `custom_components/music_assistant_alexa_voice` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration from **Settings → Devices & Services**

### 3. Configure the integration

| Setting | Value |
|---|---|
| **Add-on URL** | `http://music_assistant_alexa_voice:5000` (default) |
| **Cloud access token** | Create a long random secret string. Alexa will include this in requests. |

The integration validates connectivity by calling the add-on `/health` endpoint, so start the add-on first.

### 4. Alexa skill endpoint

Use your Home Assistant Cloud URL plus the integration path:

```text
https://YOUR_ID.ui.nabu.casa/api/music_assistant_alexa_voice/alexa?token=YOUR_CLOUD_ACCESS_TOKEN
```

In the Alexa Developer Console:

1. **Build → Endpoint**
2. Type: **HTTPS**
3. URL: the full URL above
4. Certificate: **My development endpoint is a sub-domain...** (Amazon trust for `*.ui.nabu.casa`)

You do **not** need to expose add-on port 5000 to the internet when using Home Assistant Cloud.

### 5. Create the Alexa skill

Import `music_assistant_alexa_voice/skill/interaction-model/en-US.json` and set invocation name to `music assistant`. See the [main README](../README.md) for the full Alexa Developer Console checklist.

## Example utterances

- "Alexa, open music assistant"
- "Alexa, ask music assistant to play Fleetwood Mac"
- "Alexa, ask music assistant to play jazz in the kitchen"
- "Alexa, ask music assistant to pause"

## Troubleshooting

| Issue | Fix |
|---|---|
| Add-on repo added but nothing appears | Use the `main` branch URL with no `#branch` suffix. Supervisor cannot use branch names containing `/`. Remove the repo, add `https://github.com/Shaffer-Softworks/music-assistant-alexa-voice`, then refresh the add-on store |
| Add-on fails to start | Set `ma_token` and `default_player_id` in the add-on configuration |
| Integration cannot connect | Start the add-on first and confirm the default add-on URL works internally |
| Alexa gets 401 | Verify the `token=` query parameter matches the integration access token |
| Alexa gets 503 | Check add-on logs; the integration could not reach the add-on |
| Cannot reach Music Assistant | Confirm the Music Assistant add-on is running and `ma_url` uses the correct internal slug |
| `/players` returns an error | Check the API token and MA URL from the add-on logs |

## Standalone Docker

You can also run outside Home Assistant with Docker Compose — see [README.md](../README.md) in the repository root.
