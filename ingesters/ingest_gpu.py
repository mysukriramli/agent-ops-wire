import logging
import urllib.parse
import requests
from ingesters.utils import save_wire_data

logger = logging.getLogger("OpsWire.GPU")

def run():
    # Vast.ai public unauthenticated API for verified, available spot instances
    query = '{"gpu_name":{"in":["RTX 4090", "A100", "A100 SXM4", "H100"]},"verified":{"eq":true},"allocated":{"eq":false}}'
    encoded = urllib.parse.quote(query)
    url = f"https://console.vast.ai/api/v0/bundles/?q={encoded}"
    
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        offers = res.json().get("offers", [])
        
        # Group lowest price by GPU model
        cheapest_gpus = {}
        for offer in offers:
            name = offer.get("gpu_name")
            dph = offer.get("dph_total") # Dollars per hour
            if name and dph:
                if name not in cheapest_gpus or dph < cheapest_gpus[name]["price_usd_per_hour"]:
                    cheapest_gpus[name] = {
                        "gpu_model": name,
                        "price_usd_per_hour": round(dph, 3),
                        "cuda_max_good": offer.get("cuda_max_good"),
                        "provider_machine_id": offer.get("machine_id")
                    }
        
        items = list(cheapest_gpus.values())
        md_lines = ["# Decentralized GPU Spot Pricing", "## Lowest Hourly Rates for Autonomous AI Compute\n"]
        for item in sorted(items, key=lambda x: x["price_usd_per_hour"]):
            md_lines.append(f"- **{item['gpu_model']}**: ${item['price_usd_per_hour']}/hr (CUDA: {item['cuda_max_good']})")
            
        save_wire_data("gpu_market", "spot_prices", items, "\n".join(md_lines))
        logger.info(f"GPU Market Wire updated with {len(items)} models.")
    except Exception as e:
        logger.error(f"GPU Market ingestion failed: {e}")
