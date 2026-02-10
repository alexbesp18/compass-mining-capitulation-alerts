"""
Compass Mining GraphQL API client.

Endpoint: https://api.compassmining.io/graphql
Method: POST, Content-Type: application/json
Auth: None required for read queries.
"""

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import List, Optional
from .config import GRAPHQL_URL, TARGET_MODELS, POLL_LIMIT
from .models import MinerProduct


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout, requests.HTTPError)),
)
def _gql(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query. Returns the 'data' dict or raises on error."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(GRAPHQL_URL, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    if result.get("errors"):
        raise Exception(f"GraphQL errors: {result['errors']}")
    return result["data"]


def _match_target_model(model_name: str) -> Optional[str]:
    """Match a product's model name to our TARGET_MODELS keys."""
    if not model_name:
        return None
    for target in TARGET_MODELS:
        if target.lower() in model_name.lower() or model_name.lower() in target.lower():
            return target
    return None


def fetch_btc_stats() -> dict:
    """Get current BTC price and hashprice from public APIs (not Compass)."""
    try:
        price_resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            timeout=10,
        )
        price_resp.raise_for_status()
        btc_price = price_resp.json()["bitcoin"]["usd"]
    except Exception:
        btc_price = 0

    try:
        hp_data = _gql("{ getHashprice { hashpriceUsd } }")
        hashprice = float(hp_data["getHashprice"]["hashpriceUsd"])
    except Exception:
        hashprice = 0

    return {"btc_price": btc_price, "hashprice_usd": hashprice}


def fetch_model_summary() -> dict:
    """Fetch aggregated model-level data (min prices, quantities)."""
    data = _gql("""
    {
        allAvailableMinerModels(first: 100) {
            nodes {
                minerModelName
                minerModelHashratePerTerahashMax
                minerModelPowerConsumptionWattsMax
                productAvailableQuantityTotal
                productListingPriceMinHosted
                productListingPriceMinMarketplace
                productPricePerTerahashMin
                manufacturerName
                productTypes
            }
        }
    }
    """)
    models = {}
    for node in data["allAvailableMinerModels"]["nodes"]:
        name = node["minerModelName"]
        if _match_target_model(name):
            models[name] = node
    return models


def fetch_products() -> List[MinerProduct]:
    """Fetch all available products for target models."""
    all_products = []
    offset = 0

    while True:
        data = _gql("""
        query GetProducts($first: Int!, $offset: Int!) {
            allAvailableProducts(first: $first, offset: $offset) {
                totalCount
                nodes {
                    productId
                    minerModelName
                    manufacturerName
                    minerModelHashratePerTerahash
                    minerModelPowerConsumptionWatts
                    productWattsPerHashrate
                    productListingPrice
                    productPricePerHashrate
                    compassScore
                    productType
                    facilityDisplayName
                    countryName
                    monthlyHostingCharges
                    productAvailableQuantity
                    productCondition
                    productDiscountPercent
                    productDiscountReason
                    productDateListed
                    isProductFeatured
                }
            }
        }
        """, variables={"first": POLL_LIMIT, "offset": offset})

        result = data["allAvailableProducts"]
        total = result["totalCount"]

        for node in result["nodes"]:
            model_name = node["minerModelName"]
            target = _match_target_model(model_name)
            if not target:
                continue

            hashrate = float(node["minerModelHashratePerTerahash"] or 0)
            price = float(node["productListingPrice"] or 0)
            if price <= 0:
                continue

            product = MinerProduct(
                product_id=node["productId"],
                model_name=model_name,
                manufacturer=node["manufacturerName"] or "Unknown",
                hashrate_th=hashrate,
                power_watts=int(node["minerModelPowerConsumptionWatts"] or 0),
                watts_per_th=float(node["productWattsPerHashrate"] or 0),
                listing_price=price,
                price_per_th=float(node["productPricePerHashrate"] or 0),
                compass_score=float(node["compassScore"]) if node.get("compassScore") else None,
                product_type=node["productType"] or "UNKNOWN",
                facility_name=node["facilityDisplayName"],
                country=node["countryName"],
                monthly_hosting=float(node["monthlyHostingCharges"]) if node.get("monthlyHostingCharges") else None,
                available_qty=int(node["productAvailableQuantity"] or 1),
                condition=node["productCondition"],
                discount_percent=float(node["productDiscountPercent"]) if node.get("productDiscountPercent") else None,
                discount_reason=node["productDiscountReason"],
                date_listed=node["productDateListed"],
                is_featured=bool(node.get("isProductFeatured")),
                link=f"https://us.compassmining.io/mining/hardware/{node['productId']}",
            )
            all_products.append(product)

        offset += POLL_LIMIT
        if offset >= total:
            break

    return all_products
