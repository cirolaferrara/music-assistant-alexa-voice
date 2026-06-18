# Music Assistant Alexa Voice

Voice-control [Music Assistant](https://music-assistant.io) players from Alexa.

## Home Assistant add-on (recommended)

### Install

1. In Home Assistant, open **Settings → Add-ons → Add-on Store → ⋮ → Custom repositories**
2. Add this repository URL:

   ```text
   https://github.com/sickkick/music-assistant-alexa-voice
   ```

3. Refresh the add-on store and install **Music Assistant Alexa Voice**
4. Configure the add-on:

   | Option | Description |
   |---|---|
   | **Music Assistant URL** | Internal MA API URL. Default `http://08524bff_music_assistant:8095` works if you use the official Music Assistant add-on. If yours uses a different slug, open the Music Assistant add-on **Info** page and use `http://<slug>:8095`. |
   | **Music Assistant API token** | Create in MA → Settings → User management → API tokens |
   | **Default player ID** | Player ID from MA → Settings → Players |
   | **Player aliases** | Optional JSON map, e.g. `{"kitchen":"player-id","satellite":"other-id"}` |

5. Start the add-on
6. Open the add-on **Open Web UI** link (or `/players`) to verify MA connectivity and copy player IDs

### Expose to Alexa

Alexa requires a public HTTPS endpoint. Point your reverse proxy or Cloudflare Tunnel at the add-on port (default **5000**) on your Home Assistant host:

```text
https://alexa-voice.example.com/alexa
```

Then create the Alexa skill using `music_assistant_alexa_voice/skill/interaction-model/en-US.json` — see the [main README](README.md).

## Example utterances

- "Alexa, open music assistant"
- "Alexa, ask music assistant to play Fleetwood Mac"
- "Alexa, ask music assistant to play jazz in the kitchen"
- "Alexa, ask music assistant to pause"

## Troubleshooting

| Issue | Fix |
|---|---|
| Add-on fails to start | Set `ma_token` and `default_player_id` in the add-on configuration |
| Cannot reach Music Assistant | Confirm the Music Assistant add-on is running and `ma_url` uses the correct internal slug |
| `/players` returns an error | Check the API token and MA URL from the add-on logs |
| Alexa cannot reach the skill | Verify external HTTPS to port 5000 and endpoint path `/alexa` |

## Standalone Docker

You can also run outside Home Assistant with Docker Compose — see [README.md](../README.md) in the repository root.
