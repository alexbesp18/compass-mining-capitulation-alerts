from dataclasses import dataclass
from typing import Optional


@dataclass
class MinerProduct:
    product_id: str
    model_name: str
    manufacturer: str
    hashrate_th: float
    power_watts: int
    watts_per_th: float
    listing_price: float
    price_per_th: float
    compass_score: Optional[float]
    product_type: str               # HOSTED, MARKETPLACE, NON_HOSTED
    facility_name: Optional[str]
    country: Optional[str]
    monthly_hosting: Optional[float]
    available_qty: int
    condition: Optional[str]
    discount_percent: Optional[float]  # Compass-reported discount
    discount_reason: Optional[str]
    date_listed: Optional[str]
    is_featured: bool
    link: str


@dataclass
class Alert:
    product: MinerProduct
    btc_price: float
    hashprice_usd: float
    reference_price: float          # our stored reference for this model
    discount_vs_reference: float    # percent off reference price
