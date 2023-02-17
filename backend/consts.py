import os
from pathlib import Path as filePath


class Env:
    LOCAL = "LOCAL"
    DEV = "DEV"
    TESTING = "TESTING"
    PROD = "PROD"


PROJECT_ROOT = str(filePath(os.path.abspath(__file__)).parent.absolute().parent.absolute())
PDF_DIR = os.path.join(PROJECT_ROOT, "static/upload/pdf")
PDF_XML_DIR = os.path.join(PROJECT_ROOT, "static/processed/xml")
PDF_PROCESS_DIR = os.path.join(PROJECT_ROOT, "static/processed/pdf")
PDF_IMAGE_DIR = os.path.join(PROJECT_ROOT, "static/processed/pdf_image")
IMG_DIR = os.path.join(PROJECT_ROOT, "static/attachment/img")
TABLE_CONTENT_FILE_DIR = os.path.join(PROJECT_ROOT, "static/processed/table/content")

IMG_BASE_URL = "/api/v1/img"
