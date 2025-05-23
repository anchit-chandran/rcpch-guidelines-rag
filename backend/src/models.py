from typing import List
from pydantic import BaseModel


class DocumentElementMetadata(BaseModel):
	file_directory: str
	filename: str
	filetype: str
	languages: List[str]
	last_modified: str
	page_number: int

	def to_dict(self):
		return {
			"file_directory": self.file_directory,
			"filename": self.filename,
			"filetype": self.filetype,
			"last_modified": self.last_modified,
			"page_number": self.page_number,
		}


class DocumentElement(BaseModel):
	element_id: str
	metadata: DocumentElementMetadata
	text: str


class SourceDataForDocument(BaseModel):
	source_url: str
	source_name: str
	source_data: str


class SourceDataCollection(BaseModel):
	source_data: List[SourceDataForDocument]
