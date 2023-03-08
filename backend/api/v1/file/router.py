import os

from fastapi import APIRouter, File, HTTPException, Path, UploadFile, status
from fastapi.responses import FileResponse

from consts import PDF_IMAGE_DIR
from crud import pdf as pdf_handler

router = APIRouter()


@router.put("/file", description="通过上传文件导入论文")
async def add_documents_by_file(
    file: UploadFile = File(..., description="要上传的文件，目前只支持PDF或者Zip格式的文件"),
):
    if file.filename.lower().endswith(".pdf"):
        file_hash = await pdf_handler.save_pdf_file(file)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Only support PDF file or Zip file."
        )
    result = {
        "file_hash": file_hash,
    }
    return result


@router.get("/pdf_img/{paper_id}/{image_id}", response_class=FileResponse, description="获取论文图片")
async def get_images(
    paper_id: str = Path(..., description="目标论文ID", example="0acd2a0f29d190d334a8b23522c02a90"),
    image_id: str = Path(..., description="目标图片信息", example="000.jpg"),
):
    img_path = os.path.join(PDF_IMAGE_DIR, paper_id, image_id)
    if not os.path.isfile(img_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"PDF file not found.")
    return FileResponse(img_path)
