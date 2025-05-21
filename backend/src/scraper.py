from collections import defaultdict
from datetime import datetime
import json
import os
import re
from urllib.parse import urlparse
import constants as c
from bs4 import BeautifulSoup
import requests
from logger import get_logger
from pydantic import BaseModel

_logger = get_logger(__name__)


class AllLinksData(BaseModel):
    run_at_datetime: datetime
    links_by_type: dict[str, list[str]]
    links: list[str]

    def print_analysis(self):
        _logger.info(f"Found {len(self.links)} links")

        for link_type, links in self.links_by_type.items():
            _logger.info(f"{link_type}: {len(links)}")


def extract_website(url):
    netloc = urlparse(url).netloc
    match = re.match(r"(?:www\.)?([a-zA-Z0-9\-]+)", netloc)
    return match.group(1) if match else netloc


def scrape_links():
    """Use a dumb method:

    All links inside a specific div
    """
    _logger.info("Scraping links from RCPCH guidelines page")

    # Init
    response = requests.get(c.RCPCH_GUIDELINES_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links_by_type = defaultdict(list)
    ran_at_datetime = datetime.now()

    # get all links
    links = soup.find_all("a")

    # get links between start and end
    start_href = "https://www.nice.org.uk/guidance/qs39"
    end_href = "/topic/clinical-guidelines-standards"

    collecting = False
    collected_links = []
    for link in links:
        href = link.get("href")
        if href == start_href:
            collecting = True
        if collecting:
            if href == end_href:
                break
            collected_links.append(href)

            # Also add to breakdown by website
            links_by_type[extract_website(href)].append(href)

    _logger.info(f"Scraped {len(collected_links)} links from RCPCH guidelines page")

    return AllLinksData(
        run_at_datetime=ran_at_datetime,
        links_by_type=links_by_type,
        links=collected_links,
    )


def get_links_from_site_or_cache() -> AllLinksData:
    """Get links from site or cache if it exists"""

    # cache hit
    if os.path.exists(c.DATA_DIR):
        guidelines_links_path = os.path.join(c.DATA_DIR, c.RCPCH_GUIDELINES_LINKS_FILE)
        if os.path.exists(guidelines_links_path):
            _logger.info(
                f"Cache hit for RCPCH guidelines links ({guidelines_links_path}) - loading from cache"
            )
            with open(guidelines_links_path, "r") as f:
                return AllLinksData.model_validate_json(f.read())

    # scrape
    data = scrape_links()

    # cache
    with open(os.path.join(c.DATA_DIR, c.RCPCH_GUIDELINES_LINKS_FILE), "w") as f:
        f.write(data.model_dump_json())
    _logger.info(
        f"Cached RCPCH guidelines links ({c.RCPCH_GUIDELINES_LINKS_FILE}) - scraped {len(data.links)} links"
    )
    return data


def scrape_content(links: list[str]) -> list[str]:
    """Each link type requires a different scraping strategy"""


if __name__ == "__main__":
    all_links_data = get_links_from_site_or_cache()
    all_links_data.print_analysis()
