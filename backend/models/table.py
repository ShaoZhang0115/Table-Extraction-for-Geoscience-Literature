from enum import Enum
from typing import List

from .base import AcemapBaseModel


class TableDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class TableOutline(AcemapBaseModel):
    table_id: int = 0
    page: int = 0  # 项目内部page从0开始计数
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    direction: TableDirection = "up"
    confirmed: bool = False


class TableCell(AcemapBaseModel):
    # begin代表表格单元格开始的行或列序号,end代表结束的行或序号
    column_begin: int = 0
    row_begin: int = 0
    column_end: int = 0
    row_end: int = 0


class TableStructure(AcemapBaseModel):
    area: List[float] = []
    rows: List[float] = []  # collums和rows是相对于area大框的相对位置
    columns: List[float] = []
    cells: List[List[TableCell]] = []
    confirmed: bool = False


class TableContent(AcemapBaseModel):
    excel_path: str = ""
    text: List[str] = []
    confirmed: bool = False


class Table(AcemapBaseModel):
    outline: TableOutline = TableOutline()
    structure: TableStructure = TableStructure()
    content: TableContent = TableContent()
