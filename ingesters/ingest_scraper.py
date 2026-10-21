import logging
import requests
from ingesters.utils import save_wire_data

logger = logging.getLogger("OpsWire.Scraper")

DOMAINS = [
    "reddit.com", "nytimes.com", "wikipedia.org", "github.com", 
    "stackoverflow.com", "news.ycombinator.com", "medium.com"
]
AI_USER_AGENTS = ["gptbot", "claudebot", "anthropic", "ccbot", "applebot-extended", "omgilibot"]

def run():
    items = []
    md_lines = ["# Top Domain Anti-Bot & Scraper Intelligence", "## AI Crawler Policies (robots.txt)\n"]
    
    for domain in DOMAINS:
        url = f"https://{domain}/robots.txt"
        blocked_bots = []
        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code == 200:
                text = res.text.lower()
                for bot in AI_USER_AGENTS:
                    if bot in text:
                        blocked_bots.append(bot)
                        
            item = {
                "domain": domain,
                "robots_txt_accessible": res.status_code == 200,
                "explicit_ai_bot_blocks": blocked_bots
            }
            items.append(item)
            status = "Restricts AI Crawlers" if blocked_bots else "Permissive/Unknown"
            md_lines.append(f"- **{domain}**: {status} (Flags: {', '.join(blocked_bots) if blocked_bots else 'None'})")
        except Exception as e:
            logger.warning(f"Failed to fetch {domain}: {e}")

    save_wire_data("scraper_intel", "domains", items, "\n".join(md_lines))
    logger.info("Scraper Intel Wire updated.")
