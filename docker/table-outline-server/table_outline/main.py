import base64
import multiprocessing as mp
import os
from typing import List

import cv2
import numpy as np
import uvicorn
from detectron2.config import get_cfg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from predictor import VisualizationDemo

app = FastAPI(docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WINDOW_NAME = "COCO detections"
file_path = os.path.dirname(__file__)
myconfig = os.path.join(file_path, "All_X152.yaml")
mopts = ["MODEL.WEIGHTS", os.path.join(file_path, "model_final.pth")]

myconfidence_threshold = 0.9


class ImgColInfo(BaseModel):
    tablecorlist: List[List[float]] = Field(..., example=[[1, 2, 3, 4], [1, 2, 3, 5]])


class Item(BaseModel):
    base64: str = None


def setup_cfg():
    cfg = get_cfg()
    cfg.merge_from_file(myconfig)
    cfg.merge_from_list(mopts)
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = myconfidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = myconfidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = myconfidence_threshold
    cfg.freeze()
    return cfg


def base64toCv(base64_src):
    img_b64decode = base64.b64decode(base64_src)
    img_array = np.fromstring(img_b64decode, np.uint8)
    img_cv = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
    return img_cv


cfg = setup_cfg()

demo = VisualizationDemo(cfg)


@app.post("/detect", response_model=ImgColInfo)
async def parse_pdf(request_data: Item):
    finalresult = {}
    img_base64 = request_data.base64
    img = base64toCv(img_base64)
    predictions, visualized_output, final_res = demo.run_on_image(img)
    finalresult["tablecorlist"] = final_res
    return finalresult


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    uvicorn.run(app="main:app", host="0.0.0.0", port=9092, reload=False, debug=True)
