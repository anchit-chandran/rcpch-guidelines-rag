from pydantic import BaseModel


class SourceDataForDocument(BaseModel):
    source_url: str
    source_name: str
    source_data: str


class SourceDataCollection(BaseModel):
    source_data: list[SourceDataForDocument]
