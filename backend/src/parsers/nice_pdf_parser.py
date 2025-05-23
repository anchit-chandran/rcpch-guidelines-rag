# Parser and chunker for NICE PDFs
# ----------------------------------
# This module provides functionality to:
# 1. Download NICE guideline PDFs.
# 2. Parse them into structured semantic blocks using unstructured.
# 3. Chunk these blocks with metadata preserved for embeddings.
# 4. Store embeddings in a local Chroma vector store.

import json
import os
import time
import requests
from pathlib import Path
from logger import get_logger
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import CompositeElement
from unstructured.cleaners.core import clean
import constants as c
from models import (
	DocumentElement,
	DocumentElementMetadata,
	SourceDataCollection,
	SourceDataForDocument,
)


_logger = get_logger(__name__)


def get_pdf(source_data: SourceDataForDocument) -> Path:
	"""Download a PDF from a source URL if not already present"""
	pdf_url = source_data.source_data
	pdf_name = pdf_url.split("/")[-1]
	pdf_path = c.NICE_PDF_DIR / f"{pdf_name}.pdf"
	pdf_path.parent.mkdir(parents=True, exist_ok=True)
	if not pdf_path.exists():
		_logger.debug(f"Downloading {pdf_name}")
		try:
			breakpoint()
			response = requests.get(pdf_url, timeout=10)
			response.raise_for_status()
			pdf_path.write_bytes(response.content)
		except Exception as e:
			_logger.error(f"Error downloading {pdf_name}: {e}")
			return None
	else:
		_logger.debug(f"Reusing existing PDF {pdf_name}")
	return pdf_path


class NICEPDFProcessor:
	"""Process NICE guideline PDFs for RAG embedding"""

	def __init__(
		self,
	):
		pass

	def parse_and_chunk(self, pdf_path: Path) -> list[DocumentElement]:
		"""Parse PDF and chunk into documents"""
		_logger.debug(f"Parsing {pdf_path}")
		elements: list[CompositeElement] = partition_pdf(
			pdf_path, strategy="fast", chunking_strategy="basic"
		)
		return [
			DocumentElement(
				element_id=element.id,
				metadata=DocumentElementMetadata(
					file_directory=element.metadata.file_directory,
					filename=element.metadata.filename,
					filetype=element.metadata.filetype,
					languages=element.metadata.languages,
					last_modified=element.metadata.last_modified,
					page_number=element.metadata.page_number,
				),
				text=clean(
					element.text,
					extra_whitespace=True,
					dashes=True,
					bullets=True,
					trailing_punctuation=True,
				),
			)
			for element in elements
		]


def parse_nice_pdfs(source_data_collection: SourceDataCollection):
	"""Parse all source PDFs in the collection and embed"""
	processor = NICEPDFProcessor()
	for source_data in source_data_collection.source_data:
		pdf_path = get_pdf(source_data)
		if not pdf_path:
			_logger.error(f"Skipping {source_data.source_url} because it couldn't be found!")
			continue

		# Get smart chunks
		chunks = processor.parse_and_chunk(pdf_path)

		# Write to json next to that pdf
		chunk_json_path = pdf_path.with_suffix(".json")
		chunk_json_path.write_text(json.dumps([chunk.model_dump() for chunk in chunks]))

		_logger.info(f"Wrote chunks to {chunk_json_path}")


if __name__ == "__main__":
	# Load source data collection
	_logger.info("Loading source data collection")
	sdc = SourceDataCollection.model_validate_json(c.NICE_PDF_JSON_FILE.read_text())
	parse_nice_pdfs(sdc)
