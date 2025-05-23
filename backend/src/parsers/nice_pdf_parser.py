"""Parser for NICE PDFs"""

import constants as c
import json
from models import SourceDataCollection, SourceDataForDocument
import requests
from logger import get_logger

_logger = get_logger(__name__)


def parse_nice_pdfs(source_data_collection: SourceDataCollection):
	"""Parse NICE PDFs"""
	pass


def get_pdf(source_data: SourceDataForDocument):
	"""Download a PDF from a source data if not already present"""
	pdf_url = source_data.source_data
	pdf_path = c.NICE_PDF_DIR / f"{source_data.source_name}.pdf"
	if not pdf_path.exists():
		_logger.debug(f"Downloading {pdf_path} as not present")
		pdf_path.write_bytes(requests.get(pdf_url).content)
	else:
		_logger.debug(f"Skipping {pdf_path} as it already exists")

	return pdf_path


if __name__ == "__main__":
	# Read in each PDF link, save the pdf to disk if not already present
	with open(c.NICE_PDF_JSON_FILE, "r") as f:
		data = SourceDataCollection.model_validate_json(f.read())

	for source_data in data.source_data[:1]:
		pdf_path = get_pdf(source_data)
