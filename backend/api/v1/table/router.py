import json
import logging

from fastapi import APIRouter, Body, Form, HTTPException, Path, status
from fastapi.responses import FileResponse

import models
from crud import pdf as pdf_handler, table as table_handler
from .model import *

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{paper_id}/images", description="获取论文所有图片")
async def get_page_images(
    paper_id: str = Path(..., description="目标论文ID", example="0acd2a0f29d190d334a8b23522c02a90"),
):
    page2image = pdf_handler.get_page_image(paper_id)
    return page2image


@router.post("/", response_model=List[TableOutline], description="获取表格外框线")
async def get_paper_table_outline(page2image: dict = Body(...)):
    tables = table_handler.detect_table_outlines(page2image)
    result = [
        {
            "table_id": table.table_id,
            "page": table.page,
            "x1": table.x1,
            "y1": table.y1,
            "x2": table.x2,
            "y2": table.y2,
            "direction": table.direction,
            "confirmed": table.confirmed,
        }
        for table in tables
    ]
    return [models.TableOutline.parse_obj(row) for row in result]


@router.post("/{paper_id}/image_outlined", description="获取指定的表格图片")
async def get_table_outlined_picture(
    paper_id: str = Path(..., description="目标论文ID", example="0acd2a0f29d190d334a8b23522c02a90"),
    ret: dict = Body(...)
):
    table = models.Table()
    table.enable_access()
    table.outline = models.TableOutline.parse_obj(ret)
    area = [table.outline.x1, table.outline.y1, table.outline.x2, table.outline.y2]
    direction = table.outline.direction.value
    pic_base64 = table_handler.get_outlined_table_pic(paper_id, table.outline.page, area, direction)
    if pic_base64:
        return pic_base64
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Sorry, some unkown error occured, we will fix it as soon as possible.",
    )


@router.post("/{paper_id}/cell", description="获取表格内框线")
async def get_table_inner_line(
    paper_id: str = Path(..., description="目标论文ID", example="0acd2a0f29d190d334a8b23522c02a90"),
    ret: dict = Body(...)
):
    table = models.Table()
    table.enable_access()
    table.outline = models.TableOutline.parse_obj(ret)
    area = [table.outline.x1, table.outline.y1, table.outline.x2, table.outline.y2]
    direction = table.outline.direction.value
    page = table.outline.page
    meta = await table_handler.get_and_set_table_meta(paper_id, page, area, direction)
    table.structure = table_handler.detect_table_structure(meta)
    # print(table.structure.json())
    ret["fi"] = table.structure.json()
    return ret


# 这一步认为之前已识别好了内框线和外框线, 通过之前得到的内框线生成表格结构和内容,用于给前端表格内容以显示
@router.post("/{paper_id}/draw",
             description="通过之前得到的内框线生成表格结构和内容,用于给前端表格内容以显示")
async def get_innerline_and_content_to_show(
    paper_id: str = Path(..., description="目标论文ID", example="0acd2a0f29d190d334a8b23522c02a90"),
    ret: dict = Body(...),
):
    table = await table_handler.get_table(ret)
    if not table:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Table not find")
    table.enable_access()
    areas = []

    # 求外框线内的相对坐标a,b,c,d，在整个pdf中的相对位置，注意外框要加上旋转才是真正进行计算的pdf（生成了旋转的pdf）中外框的位置
    def get_trans_rec(x1, y1, x2, y2):
        area = table_handler.get_area_direction(
            table.outline.direction.value, [table.outline.x1, table.outline.y1, table.outline.x2, table.outline.y2]
        )
        width = area[2] - area[0]
        height = area[3] - area[1]
        return [area[0] + x1 * width, area[1] + y1 * height, area[0] + x2 * width, area[1] + y2 * height]

    for row in table.structure.cells:
        for col in row:
            areas.append(
                get_trans_rec(
                    table.structure.columns[col.column_begin],
                    table.structure.rows[col.row_begin],
                    table.structure.columns[col.column_end],
                    table.structure.rows[col.row_end],
                )
            )
    area = [table.outline.x1, table.outline.y1, table.outline.x2, table.outline.y2]
    direction = table.outline.direction.value
    page = table.outline.page
    meta = await table_handler.get_and_set_table_meta(paper_id, page, area, direction)
    page = meta["page"]
    pdfpath = meta["pdfpath"]
    xmlpath = meta["xmlpath"]
    texts = table_handler.get_area_text(paper_id, pdfpath, page, xmlpath, areas)
    table.content.text = texts
    table.content.confirmed = False
    rownum = len(table.structure.rows) - 1
    colnum = len(table.structure.columns) - 1
    tablecontent = []
    for i in range(rownum):
        tablecontent.append([])
        for j in range(colnum):
            tablecontent[i].append("")
    tablemerge = []
    textid = 0
    coltemp = 0
    for row in table.structure.cells:
        for col in row:
            tablecontent[col.row_begin][col.column_begin] = texts[textid]
            textid += 1
            if (col.row_end - col.row_begin) != 1 or (col.column_end - col.column_begin) != 1:
                tablemerge.append(
                    {
                        "row": col.row_begin,
                        "col": col.column_begin,
                        "rowspan": col.row_end - col.row_begin,
                        "colspan": col.column_end - col.column_begin,
                    }
                )
    return {"tableData": tablecontent, "mergeCells": tablemerge, "structure": table.structure}


@router.post("/{paper_id}/{trans_flag}/excel", description="获取表格内容，返回excel二进制")
async def get_excel_to_download(
    paper_id: str = Path(..., description="目标论文ID", example="0acd2a0f29d190d334a8b23522c02a90"),
    trans_flag: bool = Path(..., description="行列转换", example=False),
    content: str = Form(..., description="更改的表格内容", example='tableData:[["1","2","3"...]]'),
):
    table_data = json.loads(content)["tableData"]
    structure = json.loads(content)["structure"]
    structure = models.TableStructure.parse_obj(structure)
    if len(table_data) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Content data is not valid.")
    text_new = []
    for row in table_data:
        for item in row:
            if item is not None:
                text_new.append(item)
    text_new = models.TableContent.parse_obj({"text": text_new})
    excel_path = table_handler.create_table_excel(
        paper_id, structure.cells, text_new.text, confirmed=True, suffix="trans"
    )
    if not trans_flag:
        return FileResponse(excel_path)
    else:
        logger.info("需要行列变换")
        s, c = table_handler.get_trans_table_content(structure, text_new)
        excel_path = table_handler.create_table_excel(paper_id, s.cells, c, confirmed=True, suffix="trans")
    return FileResponse(excel_path)
