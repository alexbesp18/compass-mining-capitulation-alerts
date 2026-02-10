# Compass Mining Capitulation Alerts

Monitors the [Compass Mining](https://us.compassmining.io) marketplace for deeply discounted ASIC miners and sends Telegram alerts when capitulation-level deals appear.

## How It Works

1. **Fetches** all available products from Compass Mining's public GraphQL API
2. **Filters** for target SHA-256 miner models (S21, S21+, S21 Pro, S21 XP, etc.)
3. **Detects** capitulation deals using two triggers:
   - **≥40% off** historical reference price for the model
   - **≤$8/TH** absolute price threshold
4. **Sends** Telegram alerts with full deal details (price, $/TH, efficiency, location, hosting costs)
5. **Deduplicates** alerts using persistent state (won't re-alert on the same listing)

## Target Models

| Model | Max W/TH | Reference Price |
|-------|----------|----------------|
| Antminer S21 (200T) | 17.5 | $5,000 |
| Antminer S21+ (225-235T) | 16.0 | $5,500 |
| Antminer S21 Pro (234T) | 15.5 | $6,500 |
| Antminer S21 XP (270T) | 14.0 | $8,500 |
| Antminer S21 Hydro (335T) | 13.0 | $8,500 |
| Antminer S19 XP (141T) | 21.5 | $3,000 |
| WhatsMiner M66S | 19.5 | $7,000 |
| SealMiner A2 | 16.5 | $4,500 |

## Setup

### Prerequisites
- Python 3.12+
- Telegram bot token and chat ID

### Local Testing
```bash
pip install -r requirements.txt
python -m src.main  # dry run (no Telegram creds = prints to console)
```

### GitHub Actions (Production)
1. Fork/clone this repo
2. Add secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
3. The workflow runs every 10 minutes automatically

## API

Uses Compass Mining's public GraphQL API at `https://api.compassmining.io/graphql`. No authentication required for read queries.

## Architecture

```
src/
├── compass_api.py    # GraphQL client + BTC stats
├── alert_engine.py   # Discount calculations, dedup, quality filters
├── telegram_bot.py   # Alert formatting + Telegram delivery
├── config.py         # Thresholds, target models, constants
├── models.py         # Data classes
└── main.py           # Entry point
```

## Related Projects

- [blockware-capitulation-alerts](https://github.com/alexbesp18/blockware-capitulation-alerts) — Same pattern for Blockware marketplace
- [simplemining-capitulation-alerts](https://github.com/alexbesp18/simplemining-capitulation-alerts) — Same pattern for SimpleMining.io
