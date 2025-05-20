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
    breakdown_by_website: dict[str, int]
    links: list[str]

    def print_analysis(self):
        _logger.info(f"Found {len(self.links)} links")

        for website, count in self.breakdown_by_website.items():
            _logger.info(f"{website}: {count}")


def extract_website(url):
    netloc = urlparse(url).netloc
    match = re.match(r"(?:www\.)?([a-zA-Z0-9\-]+)", netloc)
    return match.group(1) if match else netloc


def write_link_to_own_file(link: str):
    _logger.info(f"Writing link to own file: {link}")
    website = extract_website(link.strip())
    if os.path.exists(os.path.join(c.DATA_DIR, "sub_dirs", f"{website}.txt")):
        with open(os.path.join(c.DATA_DIR, "sub_dirs", f"{website}.txt"), "a") as f:
            f.write(link + "\n")
    else:
        with open(os.path.join(c.DATA_DIR, "sub_dirs", f"{website}.txt"), "w") as f:
            f.write(link + "\n")


def scrape_links():
    """Use a dumb method:

    All links inside a specific div
    """
    _logger.info("Scraping links from RCPCH guidelines page")

    # Init
    response = requests.get(c.RCPCH_GUIDELINES_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    breakdown_by_website = defaultdict(int)
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

            # Write to own file
            write_link_to_own_file(href)

            # Collect breakdown by website
            breakdown_by_website[extract_website(href)] += 1

    _logger.info(f"Scraped {len(collected_links)} links from RCPCH guidelines page")

    return AllLinksData(
        run_at_datetime=ran_at_datetime,
        breakdown_by_website=breakdown_by_website,
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
    pass


if __name__ == "__main__":
    all_links_data = get_links_from_site_or_cache()
    all_links_data.print_analysis()
