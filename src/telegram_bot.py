"""
Telegram notification sender for Compass Mining alerts.
"""

import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def format_alert(alert) -> str:
    p = alert.product

    # Hosting info
    hosting_str = ""
    if p.monthly_hosting and p.monthly_hosting > 0:
        hosting_str = f"\n💵 Monthly Hosting: ${p.monthly_hosting:,.2f}"

    # Compass discount info (if reported by Compass themselves)
    compass_disc = ""
    if p.discount_percent and p.discount_percent > 0:
        reason = f" ({p.discount_reason})" if p.discount_reason else ""
        compass_disc = f"\n🏷 Compass Discount: {p.discount_percent:.0f}%{reason}"

    # Condition
    condition_str = f" | {p.condition}" if p.condition else ""

    msg = (
        f"🚨🚨🚨 <b>COMPASS CAPITULATION ALERT</b> 🚨🚨🚨\n"
        f"\n"
        f"<b>{p.model_name}</b> ({p.manufacturer})\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>${p.listing_price:,.0f}</b> ({p.product_type.replace('_', ' ').title()})\n"
        f"\n"
        f"<b>Discount:</b>\n"
        f"➤ {alert.discount_vs_reference:.0f}% off reference (${alert.reference_price:,.0f})\n"
        f"   ${p.price_per_th:.2f}/TH{compass_disc}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⛏ Hashrate: {p.hashrate_th:.0f} TH/s | ⚡ {p.watts_per_th:.1f} W/TH\n"
        f"🔌 Power: {p.power_watts:,}W{condition_str}\n"
        f"📍 {p.facility_name or 'N/A'} ({p.country or 'N/A'})\n"
        f"📦 Qty available: {p.available_qty}{hosting_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"₿ BTC: ${alert.btc_price:,.0f} | Hashprice: ${alert.hashprice_usd:.2f}/PH/day\n"
        f"\n"
        f'🔗 <a href="{p.link}">VIEW ON COMPASS</a>'
    )
    return msg


def send_alert(alert) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        p = alert.product
        print(f"[DRY RUN] {p.model_name} @ ${p.listing_price:,.0f} "
              f"(${p.price_per_th:.2f}/TH, {alert.discount_vs_reference:.0f}% off ref)")
        return True

    msg = format_alert(alert)
    resp = requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }, timeout=10)

    if resp.status_code == 200:
        return True
    else:
        print(f"Telegram error {resp.status_code}: {resp.text}")
        return False


def send_summary(total_products: int, btc_price: float, alerts_sent: int):
    print(f"[Summary] Scanned {total_products} products | BTC ${btc_price:,.0f} | "
          f"Alerts sent: {alerts_sent}")
