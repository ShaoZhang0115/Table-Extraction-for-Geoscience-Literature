from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class TableDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class TableOutline(BaseModel):
    table_id: int = Field(..., example=1)
    page: int = Field(..., description="该页码从0开始计数", example=1)  # page start with 0
    x1: float = Field(..., example=0.2)
    y1: float = Field(..., example=0.2)
    x2: float = Field(..., example=0.8)
    y2: float = Field(..., example=0.8)
    direction: TableDirection = Field(..., example="up")
    confirmed: bool = Field(..., example=False)


class TableCell(BaseModel):
    row_begin: int = Field(..., description="begin, end从0开始，且符合左闭右开原则，即[begin, end)", example=1)
    column_begin: int = Field(..., description="begin, end从0开始，且符合左闭右开原则，即[begin, end)", example=1)
    row_end: int = Field(..., description="begin, end从0开始，且符合左闭右开原则，即[begin, end)", example=2)
    column_end: int = Field(..., description="begin, end从0开始，且符合左闭右开原则，即[begin, end)", example=2)


class TableStructure(BaseModel):
    rows: List[float] = Field(..., example=[0.1, 0.3, 0.4])
    columns: List[float] = Field(..., example=[0.1, 0.3, 0.4])
    cells: List[List[TableCell]]
    confirmed: bool = Field(..., example=False)


class TableHeaderClassification(BaseModel):
    label_id: int = Field(..., example=1)
    keywords_group: str = Field(..., example="SrNd")
    description: str = Field(..., example="锶钕同位素")
    header: List[str] = Field(..., example=["Age", "Sm", "Sr"])
