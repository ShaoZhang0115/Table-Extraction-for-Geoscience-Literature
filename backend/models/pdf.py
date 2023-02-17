from typing import List

from .base import AcemapBaseModel


class PdfInfo(AcemapBaseModel):
    title: str = ""
    abstract: str = ""
    authors: List[str] = []
    affiliations: List[str] = []
    journal: str = ""
    issn: str = ""
    publisher: str = ""
    volume: int = 0
    issue: int = 0
    year: int = 0
    first_page: int = (0,)
    last_page: int = (0,)
    doi: str = ""
    content: str = ""
