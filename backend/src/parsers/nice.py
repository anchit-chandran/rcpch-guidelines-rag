"""Parser for NICE guidance"""

import json
import re
from bs4 import BeautifulSoup
import requests
from logger import get_logger
from models import SourceDataCollection, SourceDataForDocument
import constants as c

_logger = get_logger(__name__)


def parse_nice_links(links: list[str]):
    """Parse nice links

    Strategy:
    - Download the PDF
    - Encode the PDF
    - Store the PDF
    """
    res = SourceDataCollection(source_data=[])
    for link in links:
        _logger.info(f"Parsing NICE link: {link}")

        # Pages on NICE all seem a bit different but seems we can access a PDF
        # guidance on all links. Download these and for encodings
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")

        source_data_for_document = {}

        # Title
        _logger.info("Parsing title")
        title = soup.find("h1", class_="page-header__heading")
        if title:
            source_data_for_document["title"] = title.text.strip()
            _logger.info("\tFound!")
        else:
            _logger.warning("\tNo title found.")

        # Get the pdf (weird white spacing so handle that)
        pdf_element = soup.find("a", string=re.compile(r"download.+PDF", re.I))

        if pdf_element:
            if not (pdf_url := pdf_element.get("href")):
                _logger.warning("\tCould not extract PDF url from link")
            else:
                _logger.info("\tFound!")

                # chop off first bit so we can get full url
                match = re.search(r"(resources.*)", pdf_url)
                if match:
                    result = match.group(1)
                    source_data_for_document["pdf_url"] = f"{link}/{result}"

                else:
                    _logger.warning("\tCould not extract PDF url from link")
        else:
            _logger.warning("\tNo PDF link found.")

        res.source_data.append(
            SourceDataForDocument(
                source_url=link,
                source_name=source_data_for_document.get("title", ""),
                # For now just append the pdf url, we'll parse and encode later
                source_data=source_data_for_document.get("pdf_url", ""),
            )
        )
        _logger.info("Done\n\n")

    _logger.info(f"Parsed {len(res.source_data)} links")
    _logger.info(f"Writing to {c.NICE_PDF_JSON_FILE}")
    with open(c.NICE_PDF_JSON_FILE, "w") as f:
        f.write(res.model_dump_json())
    return res
