#!/usr/bin/env python3
import logging
from datetime import datetime, timezone
from ingesters import ingest_gpu, ingest_scraper, ingest_bounties

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def generate_root_llms_txt():
    now_iso = datetime.now(timezone.utc).isoformat()
    content = f"""# The Agent Operations & Economy Wire
> High-signal, machine-readable datasets for autonomous agents to buy compute, find paid work, and navigate the web safely.
> Last synchronized: {now_iso}

## 1. Global GPU Compute Market
Tracks real-time decentralized spot pricing for H100s, A100s, and RTX 4090s.
- [Active Prices JSON](data/gpu_market/today.json)
- [LLM Context Digest](data/gpu_market/llms.txt)

## 2. Web Scraper & Anti-Bot Intelligence
Tracks robots.txt updates across top domains to help web-browsing agents route around blocks.
- [Domain Policies JSON](data/scraper_intel/today.json)
- [LLM Context Digest](data/scraper_intel/llms.txt)

## 3. Autonomous AI Coding Bounties
Aggregates unassigned, paid GitHub issues globally for coding agents to hunt and solve.
- [Open Bounties JSON](data/ai_bounties/today.json)
- [LLM Context Digest](data/ai_bounties/llms.txt)
"""
    with open("llms.txt", "w", encoding="utf-8") as f:
        f.write(content)

def main():
    logging.info("Starting Agent Economy Ingestion...")
    for name, module in [("GPU Market", ingest_gpu), ("Scraper Intel", ingest_scraper), ("AI Bounties", ingest_bounties)]:
        try:
            module.run()
        except Exception as e:
            logging.error(f"Error in {name}: {e}")
            
    generate_root_llms_txt()
    logging.info("Run complete.")

if __name__ == "__main__":
    main()
