from consts import Env
from core.config import EnvironConfig

prefix = "TABLE"

ENV = EnvironConfig.get_str(f"{prefix}_ENV", Env.LOCAL)
LOG_LEVEL = EnvironConfig.get_str(f"{prefix}_LOG_LEVEL", "debug")

TABLE_DETECT_SERVER_HOST = EnvironConfig.get_str(f"{prefix}_TABLE_DETECT_SERVER_HOST", "127.0.0.1")

PDF_PARSER_BACKEND_INFO = EnvironConfig.get_dict(
    f"{prefix}_PDF_PARSER_BACKEND_INFO",
    {
        "grobid": {
            "host": "127.0.0.1",
            "port": 8074,
        }
    },
)
