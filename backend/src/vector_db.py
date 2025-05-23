"""Chromadb can take in Documents and embed itself"""

import glob
import json
from pathlib import Path
from models import DocumentElement
import constants as c
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from logger import get_logger
import rich
import tqdm

_logger = get_logger(__name__)


class VectorDB:
	def __init__(self, embedding_model_name="all-MiniLM-L6-v2"):
		self.embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)
		self.db = self._init_db()

	def _init_db(self):
		"""Initialise vectordb -> try to find existing embeddings
		- if not existing, need to run _load_chunked_data_into_documents
		"""
		if not c.EMBEDDINGS_DIR.exists():
			_logger.info("No embeddings found, loading chunked data into documents")
			return self._load_chunked_data_into_documents()

		_logger.info("Using existing embeddings")
		return Chroma(
			persist_directory=str(c.EMBEDDINGS_DIR),
			embedding_function=self.embedder,
		)

	def _load_chunked_data_into_documents(self):
		# Get all the .json files inside NICE_PDF_DIR
		chunk_json_files = glob.glob(str(c.NICE_PDF_DIR / "*.json"))

		all_documents = []

		# Show progress bar
		for pdf_chunked_json_file in tqdm.tqdm(
			chunk_json_files, desc="Loading chunked data into documents"
		):
			pdf_chunked_data = json.loads(Path(pdf_chunked_json_file).read_text())
			pdf_chunked_data = [DocumentElement.model_validate(chunk) for chunk in pdf_chunked_data]

			# Create documents
			documents = [
				Document(
					page_content=chunk.text,
					metadata={
						**chunk.metadata.to_dict(),
						"element_id": chunk.element_id,
					},
				)
				for chunk in pdf_chunked_data
			]

			all_documents.extend(documents)

		# Store documents in ChromaDB
		_logger.info(f"Creating ChromaDB with {len(all_documents)} documents")
		self.db = Chroma.from_documents(
			documents=tqdm.tqdm(all_documents, desc="Embedding documents"),
			embedding=self.embedder,
			persist_directory=str(c.EMBEDDINGS_DIR),
		)
		_logger.info("ChromaDB created")

		return self.db

	def similarity_search(self, query, k=4) -> list[tuple[Document, float]]:
		"""Search for documents similar to the query. Return (document, cos dist)"""
		if self.db is None:
			raise ValueError(
				"Database not initialized. Call load_chunked_data_into_documents first."
			)

		return self.db.similarity_search_with_score(query, k=k)

	def pretty_print_sim_search_results(self, results_and_scores: list[tuple[Document, float]]):
		"""Uses Rich to nicely print search results with improved formatting"""
		from rich.panel import Panel
		from rich.table import Table
		from rich.console import Console
		from rich.text import Text
		from rich import box
		from rich.columns import Columns

		console = Console()

		for i, (doc, score) in enumerate(results_and_scores):
			# Create a panel for each result
			panel_title = f"[bold cyan]Result #{i + 1} (Cos Dist: {score:.2f})[/bold cyan]"

			# Format the content with better truncation
			preview = doc.page_content

			# Create metadata table
			meta_table = Table(
				box=box.SIMPLE, title="[bold yellow]Metadata[/bold yellow]", expand=True
			)
			meta_table.add_column("Field", style="blue")
			meta_table.add_column("Value", style="yellow")

			# Add relevant metadata fields in a readable order
			if "filename" in doc.metadata:
				filename = doc.metadata["filename"]
				meta_table.add_row("File", filename)

			if "page_number" in doc.metadata:
				meta_table.add_row("Page", str(doc.metadata["page_number"]))

			if "element_id" in doc.metadata:
				element_id = doc.metadata["element_id"]
				short_id = element_id[:8] + "..." if len(element_id) > 8 else element_id
				meta_table.add_row("Element ID", short_id)

			# Add any remaining metadata that wasn't explicitly handled
			for key, value in doc.metadata.items():
				if key not in ["filename", "page_number", "element_id"]:
					if isinstance(value, str) and len(value) > 50:
						value = value[:47] + "..."
					meta_table.add_row(key.replace("_", " ").title(), str(value))

			# Create a combined layout with content and metadata
			content_text = Text(preview, style="green")

			# Create the main panel with all content inside
			panel = Panel(
				Columns([content_text, meta_table]),
				title=panel_title,
				border_style="cyan",
				padding=(1, 2),
			)

			console.print(panel)
			console.print()  # Empty line for separation


if __name__ == "__main__":
	vector_db = VectorDB()

	print(f"Loaded {vector_db.db._collection.count()} documents into ChromaDB")

	# Example search
	query = input("Enter query: ")
	results_and_scores = vector_db.similarity_search(query, k=10)
	vector_db.pretty_print_sim_search_results(results_and_scores)
