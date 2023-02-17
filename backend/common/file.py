import hashlib

from fastapi import UploadFile as _UploadFile

CHUNK_SIZE = 1024 * 1024


def get_bytes_hash(content):
    md5 = hashlib.md5()
    md5.update(content)
    return md5.hexdigest()


def get_file_hash(filename):
    md5 = hashlib.md5()
    with open(filename, "rb") as fp:
        while content := fp.read(CHUNK_SIZE):
            md5.update(content)
        return md5.hexdigest()


async def get_upload_file_hash(file: _UploadFile) -> str:
    """
    Get MD5 of a file uploaded by post request.

    :param file: The file object.
    :return: MD5 value.
    """

    await file.seek(0)
    md5 = hashlib.md5()
    while content := await file.read(CHUNK_SIZE):
        md5.update(content)
    return md5.hexdigest()
