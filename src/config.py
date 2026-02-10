GRAPHQL_URL = "https://api.compassmining.io/graphql"

# Alert thresholds
DISCOUNT_THRESHOLD = 40          # percent off historical high $/TH for the model
LOW_DOLLAR_PER_TH = 8.0         # absolute $/TH threshold — alert if below this
MAX_EFFICIENCY_WTH = 25.0       # skip offers above this W/TH (filters old-gen junk)
MIN_COMPASS_SCORE = 0           # minimum compass score (0 = no filter; their scoring is inconsistent)

POLL_LIMIT = 100  # max products per query page

# Target SHA-256 miner models (new-gen focus).
# We track by name substring match since Compass uses UUIDs, not stable integer IDs.
TARGET_MODELS = {
    "Antminer S21":       {"max_wth": 17.5, "reference_price": 5000},
    "Antminer S21+":      {"max_wth": 16.0, "reference_price": 5500},
    "Antminer S21 Pro":   {"max_wth": 15.5, "reference_price": 6500},
    "Antminer S21 XP":    {"max_wth": 14.0, "reference_price": 8500},
    "Antminer S21 Hydro": {"max_wth": 13.0, "reference_price": 8500},
    "Antminer S19 XP":    {"max_wth": 21.5, "reference_price": 3000},
    "Antminer S19j Pro":  {"max_wth": 29.5, "reference_price": 2500},
    "Antminer S19j Pro+": {"max_wth": 24.0, "reference_price": 3000},
    "WhatsMiner M66S":    {"max_wth": 19.5, "reference_price": 7000},
    "WhatsMiner M56S":    {"max_wth": 22.0, "reference_price": 4000},
    "SealMiner A2":       {"max_wth": 16.5, "reference_price": 4500},
}

SENT_ALERTS_PATH = "data/sent_alerts.json"
