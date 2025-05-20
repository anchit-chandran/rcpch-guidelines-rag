import constants as c
from bs4 import BeautifulSoup
import requests


def scrape_links() -> list[str]:
    response = requests.get(c.RCPCH_GUIDELINES_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    return [link.get("href") for link in links]


def scrape_content(links: list[str]) -> list[str]:
    pass
