import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict

import fitz
import requests
from PIL import Image
from fastapi import UploadFile as _UploadFile
from lxml import etree

import models, settings
from common import get_upload_file_hash
from consts import PDF_DIR, PDF_IMAGE_DIR, PDF_XML_DIR

logger = logging.getLogger(__name__)


def get_page_image(hash_value: str) -> Dict[int, str]:
    pdf_path = os.path.join(PDF_DIR, f"{hash_value}.pdf")
    img_pages = get_images_from_pdf(pdf_path)
    result = {}
    os.makedirs(os.path.join(PDF_IMAGE_DIR, hash_value), exist_ok=True)
    for page, img in enumerate(img_pages):
        image_id = os.path.join(hash_value, f"{page:03d}.jpg")
        image_path = os.path.join(PDF_IMAGE_DIR, image_id)
        img.save(image_path)
        result[page] = image_id
    return result


def get_images_from_pdf(pdfpath, density=2300):
    doc = fitz.open(pdfpath)
    page_number = len(doc)
    images = []
    for page in range(page_number):
        page = doc[page]
        pix = page.getPixmap()
        pdfheight = pix.height
        pdfwidth = pix.width
        pdfzoom = min(density / pdfheight, density / pdfwidth)
        mat = fitz.Matrix(pdfzoom, pdfzoom).preRotate(0)
        pix = page.getPixmap(matrix=mat, alpha=False)
        pix = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(pix)
    return images


async def save_pdf_file(file: _UploadFile) -> str:
    hash_value = await get_upload_file_hash(file)
    await file.seek(0)
    file_path = os.path.join(PDF_DIR, f"{hash_value}.pdf")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return hash_value


def _walk(node, text_list):
    tag = etree.QName(node).localname

    if node.text:
        if tag in ["head", "p"]:
            text_list.append(node.text)

    for child in node:
        _walk(child, text_list)


def _int_or_0(s: str):
    try:
        return int(s)
    except:
        return 0


def _get_first(array: list):
    return array[0] if array else etree.Element("fake")


def _get_pdf_info(hash_value: str) -> models.PdfInfo:
    """
    Get title, abstract, author, affiliation, main_text of the pdf file.
    Exception raised while the xml file does not exist.

    :param hash_value: The md5 value of pdf file.
    :return: A dict contains the information of PDF file.
    :exception: AcemapException with error information.
    """

    xml_file_path = os.path.join(PDF_XML_DIR, f"{hash_value}.grobid.xml")
    assert os.path.exists(xml_file_path)

    root = etree.parse(xml_file_path).getroot()
    text_list = []
    _walk(root, text_list)

    ns = root.nsmap
    ns["ns"] = ns[None]
    ns.pop(None)

    title = "".join(root.xpath("//ns:titleStmt/ns:title//text()", namespaces=ns))
    abstract = "".join(root.xpath("//ns:abstract//text()", namespaces=ns)).strip()

    author_elements = root.xpath("//ns:teiHeader//ns:author/ns:persName", namespaces=ns)
    authors = []
    for author_element in author_elements:
        forename = " ".join(author_element.xpath(".//ns:forename//text()", namespaces=ns)).strip()
        surname = " ".join(author_element.xpath(".//ns:surname//text()", namespaces=ns)).strip()
        name = "%s %s" % (forename, surname)
        name = re.sub(r"\s+", " ", name)
        authors.append(name)

    aff_elements = root.xpath('//ns:teiHeader//ns:author//ns:orgName[@type="institution"]', namespaces=ns)
    affiliations = []
    for aff_element in aff_elements:
        name = " ".join(aff_element.xpath(".//text()")).strip()
        affiliations.append(name)

    journal = "".join(
        root.xpath('//ns:teiHeader//ns:biblStruct//ns:monogr//ns:title[@type="main"]//text()', namespaces=ns)
    ).strip()
    issn = "".join(
        root.xpath('//ns:teiHeader//ns:biblStruct//ns:monogr//ns:idno[@type="ISSN"]//text()', namespaces=ns)
    ).strip()
    publisher = "".join(
        root.xpath("//ns:teiHeader//ns:biblStruct//ns:monogr//ns:publisher//text()", namespaces=ns)
    ).strip()
    volume = _int_or_0(
        "".join(
            root.xpath('//ns:teiHeader//ns:biblStruct//ns:monogr//ns:biblScope[@unit="volume"]//text()', namespaces=ns)
        ).strip()
    )
    issue = _int_or_0(
        "".join(
            root.xpath('//ns:teiHeader//ns:biblStruct//ns:monogr//ns:biblScope[@unit="issue"]//text()', namespaces=ns)
        ).strip()
    )
    page_element = _get_first(
        root.xpath('//ns:teiHeader//ns:biblStruct//ns:monogr//ns:biblScope[@unit="page"]', namespaces=ns)
    )
    if page_element.get("from"):
        first_page = _int_or_0(page_element.get("from", 0))
        last_page = _int_or_0(page_element.get("to", 0))
    else:
        first_page = last_page = _int_or_0("".join(page_element.xpath(".//text()")).strip())
    date_element = _get_first(root.xpath("//ns:teiHeader//ns:biblStruct//ns:monogr//ns:date", namespaces=ns))
    year = _int_or_0(date_element.get("when", 0))
    doi = "".join(root.xpath('//ns:teiHeader//ns:biblStruct//ns:idno[@type="DOI"]//text()', namespaces=ns)).strip()

    info = {
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "affiliations": list(set(affiliations)),
        "journal": journal,
        "issn": issn,
        "publisher": publisher,
        "volume": volume,
        "issue": issue,
        "year": year,
        "first_page": first_page,
        "last_page": last_page,
        "doi": doi,
        "content": " ".join(text_list),
    }
    return models.PdfInfo.parse_obj(info)


def grobid_text(pdf_path: str, **kwargs) -> str:
    file_path = Path(pdf_path)
    files = {"input": (file_path.name, file_path.open("rb"), "application/pdf", {"Expires": "0"})}
    host = settings.PDF_PARSER_BACKEND_INFO["grobid"]["host"]
    port = settings.PDF_PARSER_BACKEND_INFO["grobid"]["port"]
    url = f"http://{host}:{port}/api/processFulltextDocument"
    data = {}
    if kwargs.get("generateIDs", False):
        data["generateIDs"] = "1"
    if kwargs.get("consolidate_header", False):
        data["consolidateHeader"] = "1"
    if kwargs.get("consolidate_citations", False):
        data["consolidateCitations"] = "1"
    if kwargs.get("teiCoordinates", False):
        data["teiCoordinates"] = ["persName", "figure", "ref", "biblStruct", "formula"]
    r = requests.post(url=url, data=data, files=files, headers={"Accept": "application/xml"})
    if r.status_code == 200:  # success
        content = r.content
    else:  # not 503 means fatal error, do not re-try, return directly
        content = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<TEI xml:space="preserve" xmlns="http://www.tei-c.org/ns/1.0" \n'
            b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            b'xsi:schemaLocation="http://www.tei-c.org/ns/1.0 /opt/grobid/grobid-home/schemas/xsd/Grobid.xsd"\n'
            b'xmlns:xlink="http://www.w3.org/1999/xlink"/>'
        )
        logger.error(f"PDF Grobid parse failed: {file_path.name} with http code {r.status_code}")
    return content


def parse_pdf(hash_value: str):
    xml_file_path = os.path.join(PDF_XML_DIR, f"{hash_value}.grobid.xml")
    if not os.path.exists(xml_file_path):
        pdf_file_path = os.path.join(PDF_DIR, f"{hash_value}.pdf")
        assert os.path.exists(pdf_file_path)
        fake_xml = grobid_text(pdf_file_path)
        with open(xml_file_path, "w", encoding="utf-8") as fp:
            fp.write(fake_xml)
    return _get_pdf_info(hash_value)
