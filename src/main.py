"""
Main entry point. Called by GitHub Actions every 10 minutes.
"""

import sys
from .compass_api import fetch_btc_stats, fetch_products
from .alert_engine import find_capitulation_deals, mark_alerts_sent
from .telegram_bot import send_alert, send_summary


def main():
    print("=" * 60)
    print("Compass Mining Capitulation Alert Bot - Starting run")
    print("=" * 60)

    # 1. Get BTC context
    print("[1/3] Fetching Bitcoin stats...")
    try:
        btc_stats = fetch_btc_stats()
    except Exception as e:
        print(f"ERROR fetching BTC stats: {e}")
        sys.exit(1)

    btc_price = btc_stats["btc_price"]
    hashprice = btc_stats["hashprice_usd"]
    print(f"  BTC: ${btc_price:,.2f} | Hashprice: ${hashprice}/PH/day")

    # 2. Get all current products
    print("[2/3] Fetching Compass products...")
    try:
        products = fetch_products()
    except Exception as e:
        print(f"ERROR fetching products: {e}")
        sys.exit(1)

    print(f"  Found {len(products)} target-model products")

    # 3. Find capitulation deals
    print("[3/3] Scanning for capitulation deals...")
    alerts = find_capitulation_deals(products, btc_price, hashprice)

    if not alerts:
        print("  No capitulation deals found this run.")
    else:
        print(f"  FOUND {len(alerts)} CAPITULATION DEAL(S)!")
        sent_alerts = []
        for alert in alerts:
            p = alert.product
            print(f"  -> {p.model_name} @ ${p.listing_price:,.0f} "
                  f"(${p.price_per_th:.2f}/TH, {alert.discount_vs_reference:.0f}% off ref)")
            if send_alert(alert):
                sent_alerts.append(alert)

        if sent_alerts:
            mark_alerts_sent(sent_alerts)
        print(f"  Sent {len(sent_alerts)}/{len(alerts)} alerts to Telegram")

    send_summary(len(products), btc_price, len(alerts))
    print("Done.")


if __name__ == "__main__":
    main()
