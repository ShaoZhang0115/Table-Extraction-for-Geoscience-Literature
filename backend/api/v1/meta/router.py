from fastapi import APIRouter, Path

from crud import pdf as pdf_handler
from models import PdfInfo

router = APIRouter()


@router.get("/{paper_id}/", response_model=PdfInfo, description="获取meta信息")
async def get_paper_meta(
    paper_id: str = Path(..., description="目标论文ID", example="2d389e499d8ddd241f232c0f313d30e5"),
):
    paper_meta = pdf_handler.parse_pdf(paper_id)
    return paper_meta
