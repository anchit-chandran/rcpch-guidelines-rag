import constants as c
from bs4 import BeautifulSoup
import requests
from logger import get_logger

_logger = get_logger(__name__)


def scrape_links() -> list[str]:
    response = requests.get(c.RCPCH_GUIDELINES_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    return [link.get("href") for link in links]


def scrape_content(links: list[str]) -> list[str]:
    pass


if __name__ == "__main__":
    links = scrape_links()
    print(links)
