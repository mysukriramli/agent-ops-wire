import os
import logging
import requests
from ingesters.utils import save_wire_data

logger = logging.getLogger("OpsWire.Bounties")

def run():
    # Fetch 30 most recent unassigned open issues labeled 'bounty'
    url = "https://api.github.com/search/issues?q=is:open+label:bounty+no:assignee&sort=created&order=desc&per_page=30"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        issues = res.json().get("items", [])
        
        items = []
        md_lines = ["# Autonomous AI Coding Bounties", "## Open Unassigned Paid Tasks\n"]
        
        for issue in issues:
            repo_url = issue.get("repository_url", "").replace("https://api.github.com/repos/", "")
            item = {
                "id": issue.get("id"),
                "repository": repo_url,
                "title": issue.get("title"),
                "url": issue.get("html_url"),
                "created_at": issue.get("created_at")
            }
            items.append(item)
            md_lines.append(f"- **{item['repository']}**: [{item['title']}]({item['url']}) (Opened: {item['created_at']})")
            
        save_wire_data("ai_bounties", "open_tasks", items, "\n".join(md_lines))
        logger.info(f"AI Bounties Wire updated with {len(items)} tasks.")
    except Exception as e:
        logger.error(f"Bounties ingestion failed: {e}")
