"""
Alert logic for Compass Mining capitulation deals.

Since Compass doesn't expose trade history like Blockware, we use:
1. Reference prices (historical highs from config) as benchmark
2. Absolute $/TH thresholds
3. Compass-reported discounts as supplementary signal

Triggers:
- >= DISCOUNT_THRESHOLD% off reference price for the model, OR
- $/TH below LOW_DOLLAR_PER_TH absolute threshold
Plus quality gates: efficiency and minimum price > 0.
"""

import json
import os
from typing import List, Dict
from .models import MinerProduct, Alert
from .config import (
    TARGET_MODELS, DISCOUNT_THRESHOLD, LOW_DOLLAR_PER_TH,
    MAX_EFFICIENCY_WTH, SENT_ALERTS_PATH,
)


def load_sent_alerts() -> set:
    if os.path.exists(SENT_ALERTS_PATH):
        with open(SENT_ALERTS_PATH, "r") as f:
            data = json.load(f)
            return set(data.get("sent_ids", []))
    return set()


def save_sent_alerts(sent_ids: set):
    os.makedirs(os.path.dirname(SENT_ALERTS_PATH), exist_ok=True)
    trimmed = sorted(sent_ids)[-2000:]
    with open(SENT_ALERTS_PATH, "w") as f:
        json.dump({"sent_ids": trimmed}, f)


def _match_target(model_name: str) -> str | None:
    for target in TARGET_MODELS:
        if target.lower() in model_name.lower() or model_name.lower() in target.lower():
            return target
    return None


def find_capitulation_deals(
    products: List[MinerProduct],
    btc_price: float,
    hashprice_usd: float,
) -> List[Alert]:
    sent_ids = load_sent_alerts()
    alerts = []

    for product in products:
        if product.product_id in sent_ids:
            continue

        # Quality gate: efficiency
        if product.watts_per_th > MAX_EFFICIENCY_WTH:
            continue

        target = _match_target(product.model_name)
        if not target:
            continue

        ref_price = TARGET_MODELS[target]["reference_price"]
        discount_vs_ref = round((1 - product.listing_price / ref_price) * 100, 1) if ref_price > 0 else 0

        # Trigger: deep discount off reference OR absolute $/TH bargain
        triggered = False
        if discount_vs_ref >= DISCOUNT_THRESHOLD:
            triggered = True
        if product.price_per_th > 0 and product.price_per_th <= LOW_DOLLAR_PER_TH:
            triggered = True

        if not triggered:
            continue

        alerts.append(Alert(
            product=product,
            btc_price=btc_price,
            hashprice_usd=hashprice_usd,
            reference_price=ref_price,
            discount_vs_reference=discount_vs_ref,
        ))

    # Sort by $/TH ascending (best deals first)
    alerts.sort(key=lambda a: a.product.price_per_th if a.product.price_per_th > 0 else 9999)
    return alerts


def mark_alerts_sent(alerts: List[Alert]):
    sent_ids = load_sent_alerts()
    for alert in alerts:
        sent_ids.add(alert.product.product_id)
    save_sent_alerts(sent_ids)
